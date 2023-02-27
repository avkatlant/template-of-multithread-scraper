import json
import re
from abc import ABC, abstractmethod

from lxml.html import fromstring
from requests.models import Response

from common.smart_request import SmartRequest

IP_PORT_PATTERN = re.compile(
    r"(?P<ip>(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)).*?(?P<port>\d{2,5})"
)


class Provider(ABC):
    """Request handler for a provider."""

    def __init__(self) -> None:
        self._result: set[str] = set()
        self._request = SmartRequest()

    @abstractmethod
    def create_pages_urls(self) -> list[str]:
        """Creating a list of urls of pages from which you need to parse the proxy.

        Returns:
            list[str]: List of page urls.
        """
        pass

    @abstractmethod
    def parsing(self, resp: Response) -> list[str]:
        """Parsing the data from the received response.

        Args:
            resp (Response): The response received from the request to the page.

        Returns:
            list[str]: Proxy list.
        """
        pass

    @property
    def result(self) -> list[str]:
        return list(self._result)

    def __call__(self) -> list[str]:
        self._run()
        return self.result

    def _add_to_result(self, value: str | list[str]) -> None:
        """Adding data to the result.

        Args:
            value (str | list[str]): Data to add.
        """
        if isinstance(value, str):
            mo = IP_PORT_PATTERN.search(value)
            if mo:
                self._result.add(mo.group())
        elif isinstance(value, list):
            for item in value:
                mo = IP_PORT_PATTERN.search(item)
                if mo:
                    self._result.add(mo.group())

    def _run(self) -> None:
        pages_urls = self.create_pages_urls()
        for url in pages_urls:
            resp = self._request(url=url, timeout=5, retry=7, allow_redirects=False)
            if resp:
                result = self.parsing(resp)
                self._add_to_result(result)


class FreeproxylistProxies(Provider):
    """Getting a proxy from freeproxylist.ru"""

    def create_pages_urls(self) -> list[str]:
        base_url = "https://freeproxylist.ru/protocol"
        urls_http = [f"{base_url}/http?page={num}" for num in range(1, 11)]
        urls_https = [f"{base_url}/https?page={num}" for num in range(1, 11)]
        return [*urls_http, *urls_https]

    def parsing(self, resp: Response) -> list[str]:
        result: list[str] = []
        root = fromstring(resp.content.decode("utf-8"))
        row_list = root.xpath("//tbody[@class='table-proxy-list']/tr")
        for row in row_list:
            ip = row[0].text
            port = row[1].text
            result.append(f"{ip}:{port}")
        return result


class SslproxiesProxies(Provider):
    """Getting a proxy from www.sslproxies.org"""

    def create_pages_urls(self) -> list[str]:
        return ["https://www.sslproxies.org/"]

    def parsing(self, resp: Response) -> list[str]:
        result: list[str] = []
        root = fromstring(resp.content.decode("utf-8"))
        row_list = root.xpath("//table[contains(@class,'table')]//tbody/tr")
        for row in row_list:
            ip = row[0].text
            port = row[1].text
            result.append(f"{ip}:{port}")
        return result


class FatezeroProxies(Provider):
    """Getting a proxy from proxylist.fatezero.org"""

    def create_pages_urls(self) -> list[str]:
        return ["http://proxylist.fatezero.org/proxy.list"]

    def parsing(self, resp: Response) -> list[str]:
        result: list[str] = []
        rows = resp.text.split("\n")
        for row in rows:
            if row:
                data = json.loads(row)
                host = data["host"]
                port = data["port"]
                result.append(f"{host}:{port}")
        return result


class Api89ipcnProxies(Provider):
    """Getting a proxy from http://api.89ip.cn/tqdl.html?api=1&num=9999"""

    def create_pages_urls(self) -> list[str]:
        max_num = 9999
        return [f"http://api.89ip.cn/tqdl.html?api=1&num={max_num}"]

    def parsing(self, resp: Response) -> list[str]:
        result: list[str] = []
        html = resp.text
        ip_address = re.compile(r"([\d:\.]*)<br>")
        hosts_ports = ip_address.findall(html)
        for addr in hosts_ports:
            addr_split = addr.split(":")
            if len(addr_split) == 2:
                host = addr_split[0]
                port = addr_split[1]
                result.append(f"{host}:{port}")
        return result


class XsdailiProxies(Provider):
    """Getting a proxy from www.xsdaili.cn"""

    def create_pages_urls(self) -> list[str]:
        pages_urls: list[str] = []
        base_url = "https://www.xsdaili.cn"
        pagi_urls_list = [f"{base_url}/dayProxy/{num}.html" for num in range(1, 3)]

        for pagi_url in pagi_urls_list:
            resp = self._request(url=pagi_url, timeout=5)
            if resp:
                root = fromstring(resp.content.decode("utf-8"))
                root.make_links_absolute(pagi_url)
                url_list = root.xpath(
                    "//div[contains(@class, 'table table-hover panel-default panel ips')]/div[@class='title']/a/@href"
                )

                for url in url_list:
                    pages_urls.append(url)

        return pages_urls

    def parsing(self, resp: Response) -> list[str]:
        result: list[str] = []
        root = fromstring(resp.content.decode("utf-8"))
        rows_list = root.xpath("//div[@class='cont']/text()")
        for row in rows_list:
            mo = IP_PORT_PATTERN.search(row)
            if mo:
                result.append(mo.group())
        return result


class GithubAccountProxies(Provider):
    """Getting a proxy from a github accounts."""

    def create_pages_urls(self) -> list[str]:
        return [
            # https://proxylist.to (https://github.com/proxylist-to/proxy-list/blob/main/http.txt)
            "https://github.com/proxylist-to/proxy-list/blob/main/http.txt"
            # https://github.com/parserpp/ip_ports
            "https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.txt",
            "https://cdn.jsdelivr.net/gh/parserpp/ip_ports/proxyinfo.txt",
            "https://fastly.jsdelivr.net/gh/parserpp/ip_ports@main/proxyinfo.txt",
            "https://github.rc1844.workers.dev/parserpp/ip_ports/raw/main/proxyinfo.txt",
            # https://github.com/monosans/proxy-list
            "https://github.com/monosans/proxy-list/blob/main/proxies/http.txt",
            # https://github.com/manuGMG/proxy-365
            "https://github.com/manuGMG/proxy-365/blob/main/SOCKS5.txt",
            # https://github.com/rdavydov/proxy-list
            "https://github.com/rdavydov/proxy-list/blob/main/proxies/http.txt",
            # https://github.com/hanwayTech/free-proxy-list
            "https://github.com/hanwayTech/free-proxy-list/blob/main/http.txt",
            # https://github.com/mmpx12/proxy-list
            "https://github.com/mmpx12/proxy-list/blob/master/proxies.txt",
            # # # https://github.com/yemixzy/proxy-list
            "https://github.com/yemixzy/proxy-list/blob/main/proxy-list/not_checked.txt",
            # https://github.com/ReCaree/proxy-scrapper
            "https://raw.githubusercontent.com/ReCaree/proxy-scrapper/master/proxy/http-removed.txt",
            # https://github.com/jetkai/proxy-list
            "https://github.com/jetkai/proxy-list/blob/main/online-proxies/txt/proxies.txt",
        ]

    def parsing(self, resp: Response) -> list[str]:
        result: list[str] = []
        html = resp.content.decode("utf-8")
        list_of_tuple_host_port = re.findall(IP_PORT_PATTERN, html)
        for item in list_of_tuple_host_port:
            result.append(f"{item[0]}:{item[1]}")
        return result


PROVIDERS: list[Provider] = [
    FreeproxylistProxies(),
    SslproxiesProxies(),
    FatezeroProxies(),
    Api89ipcnProxies(),
    XsdailiProxies(),
    GithubAccountProxies(),
]
