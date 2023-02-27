from common.smart_request import SmartRequest

JUDGES_LIST = [
    "http://httpbin.org/get?show_env",
    "http://www.proxy-listen.de/azenv.php",
    "https://www2.htw-dresden.de/~beck/cgi-bin/env.cgi",
    "http://www.meow.org.uk/cgi-bin/env.pl",
    "http://www.wfuchs.de/azenv.php",
    "http://wfuchs.de/azenv.php",
    "https://users.ugent.be/~bfdwever/start/env.cgi",
    "http://www.suave.net/~dave/cgi/env.cgi",
    "http://www.cknuckles.com/cgi/env.cgi",
    "http://httpheader.net",
    "http://kheper.csoft.net/stuff/env.cgi",
    "http://proxyjudge.us",
    "http://www.proxyjudge.biz",
    "http://azenv.net",
    "https://www.andrews.edu/~bidwell/examples/env.cgi",
    "http://shinh.org/env.cgi",
    "http://users.on.net/~emerson/env/env.pl",
    "http://www.9ravens.com/env.cgi",
    "http://www2t.biglobe.ne.jp/~take52/test/env.cgi",
    "http://www3.wind.ne.jp/hassii/env.cgi",
    "http://xrea.fukuyan.net/env.cgi",
]


class CheckerProxy:
    """Checking the proxy for life.

    url_of_second_check (str | None): Additional verification on a specific site. Defaults to None.
    """

    def __init__(self, url_of_second_check: str | None = None) -> None:
        self._request = SmartRequest()
        self.judges = JUDGES_LIST
        self.url_of_second_check = url_of_second_check

    def get_checked_judges(self) -> list[str]:
        """Get the list of url checked proxy judges."""
        result = []
        for item in self.judges:
            resp = self._request(url=item, timeout=1, allow_redirects=False)
            if resp and resp.status_code == 200:
                result.append(item)

        return result

    def checker(self, proxy: str) -> bool:
        proxies_dict = {"http": "http://" + proxy, "https": "http://" + proxy}
        try:
            for judge in self.get_checked_judges():
                resp = self._request(url=judge, proxies=proxies_dict, timeout=3, allow_redirects=False)

                if resp and resp.status_code == 200:
                    if not self.url_of_second_check:
                        return True

                    resp_second_check = self._request(
                        url=self.url_of_second_check, proxies=proxies_dict, timeout=6, allow_redirects=False
                    )
                    if resp_second_check and resp_second_check.status_code == 200:
                        return True

        except Exception:
            pass

        return False

    def __call__(self, proxy: str) -> bool:
        return self.checker(proxy)
