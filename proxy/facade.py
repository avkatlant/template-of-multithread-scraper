from logging import Logger

from common.logger import get_main_logger

from .checker import CheckerProxy
from .providers import PROVIDERS
from .run_threads import RunThreads

logger: Logger = get_main_logger()


class Facade:
    def __init__(self, url_of_second_check: str, max_workers_proxies: int, max_custom_worker: int) -> None:
        self.url_of_second_check = url_of_second_check
        self.max_workers_proxies = max_workers_proxies
        self.max_custom_worker = max_custom_worker

    def run(self) -> None:
        checker_proxy = CheckerProxy(url_of_second_check=self.url_of_second_check)

        rt = RunThreads(
            max_workers_proxies=self.max_workers_proxies,
            providers_list=PROVIDERS,
            checker_proxy=checker_proxy,
            max_custom_worker=self.max_custom_worker,
        )
        rt.run()
