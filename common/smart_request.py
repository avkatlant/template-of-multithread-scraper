from typing import Any

import requests
from requests.models import Response

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Referer": "https://www.google.com/",
}


class SmartRequest:
    """Request implementation with custom settings."""

    def request(
        self,
        url: str,
        method: str = "GET",
        timeout: int = 6,
        retry: int = 1,
        headers: dict[str, Any] | None = HEADERS,
        data: dict[str, Any] | None = None,
        proxies: dict[str, Any] | None = None,
        allow_redirects: bool = True,
    ) -> Response | None:
        resp = None
        cnt = 1
        while True:
            try:
                if cnt > retry:
                    break

                resp = requests.request(
                    url=url,
                    method=method,
                    headers=headers,
                    timeout=timeout,
                    data=data,
                    proxies=proxies,
                    allow_redirects=allow_redirects,
                )
                break

            except Exception:
                timeout += 1
                cnt += 1
        return resp

    def __call__(self, *args: Any, **kwargs: Any) -> Response | None:
        return self.request(*args, **kwargs)
