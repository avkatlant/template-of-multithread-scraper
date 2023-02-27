import time
from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from queue import Queue
from threading import Lock

from common.logger import get_main_logger

from .checker import CheckerProxy
from .providers import Provider

logger: Logger = get_main_logger()


class RunThreads:
    """
    This class implements an infinite run threads.
    """

    def __init__(
        self,
        max_workers_proxies: int,
        max_custom_worker: int,
        providers_list: list[Provider],
        checker_proxy: CheckerProxy,
    ) -> None:
        self._running: bool = True
        self._locker = Lock()

        self._unchecked_proxies_list: list[str] = []
        self._checked_proxies_temp: list[str] = []
        self._checked_proxies_list: list[str] = []
        self._unchecked_proxies_queue: Queue[str] = Queue()
        self._providers_queue: Queue[Provider] = Queue()
        self._count_of_completed_proxy_checks = 0

        self.max_workers_proxies: int = max_workers_proxies
        self.max_custom_worker: int = max_custom_worker
        self.providers_list = providers_list
        self.checker_proxy = checker_proxy

    def terminate(self) -> None:
        """Terminate cycles in threads."""
        self._running = False

    def report(self) -> None:
        """Report of the number of proxies processed."""
        logger.info(
            f"""
            Unchecked proxies list: {len(self._unchecked_proxies_list)}
            Checked proxies list: {len(self._checked_proxies_list)}
            _count_of_completed_proxy_checks: {self._count_of_completed_proxy_checks}
            _unchecked_proxies_queue: {self._unchecked_proxies_queue.qsize()}
            _checked_proxies_temp: {len(self._checked_proxies_temp)}
            _providers_queue: {self._providers_queue.qsize()}
            """
        )

    def getting_reports(self, time_sleep: int = 0) -> None:
        """Getting reports inside the threads."""
        while self._running:
            self.report()
            time.sleep(time_sleep)

    def create_providers_queue(self) -> None:
        """Create a queue of proxy providers."""
        while self._running:
            if len(self._unchecked_proxies_list) == 0 and self._unchecked_proxies_queue.qsize() == 0:
                for provider in self.providers_list:
                    self._providers_queue.put(provider)
            time.sleep(1)

    def get_unchecked_proxies(self) -> None:
        """Getting unchecked proxies."""
        while self._running:
            if self._providers_queue.qsize() == 0:
                time.sleep(1.2)
            else:
                provider = self._providers_queue.get()
                proxy_list: list[str] = provider()
                with self._locker:
                    self._unchecked_proxies_list.extend(proxy_list)
                    for proxy in proxy_list:
                        self._unchecked_proxies_queue.put(proxy)

    def watcher_of_proxies_check(self) -> None:
        """Watcher of proxies check threads."""
        while self._running:
            if (
                self._count_of_completed_proxy_checks == len(self._unchecked_proxies_list)
                and self._count_of_completed_proxy_checks != 0
            ):
                with self._locker:
                    self._checked_proxies_list = [*self._checked_proxies_temp]
                    self._checked_proxies_temp.clear()
                    self._unchecked_proxies_list.clear()
                    self._count_of_completed_proxy_checks = 0

    def get_checked_proxies(self) -> None:
        """Getting checked proxies."""
        while self._running:
            if self._unchecked_proxies_queue.qsize() == 0:
                time.sleep(1)
            else:
                proxy: str = self._unchecked_proxies_queue.get()
                is_good_proxy = self.checker_proxy(proxy)
                with self._locker:
                    if is_good_proxy:
                        logger.info(f"GOOD PROXY: {proxy}")
                        self._checked_proxies_temp.append(proxy)
                    self._count_of_completed_proxy_checks += 1

    def custom_worker(self) -> None:
        while self._running:
            if len(self._checked_proxies_list) == 0:
                time.sleep(1)
            else:
                # Custom Code
                pass

    def run(self) -> None:
        """Running threads."""
        count_workers = 7 + self.max_workers_proxies + self.max_custom_worker
        futures_list = []

        try:
            with ThreadPoolExecutor(max_workers=count_workers, thread_name_prefix="TH") as executor:
                futures_list = [
                    executor.submit(self.create_providers_queue),
                    *[executor.submit(self.get_unchecked_proxies) for _ in range(4)],
                    executor.submit(self.watcher_of_proxies_check),
                    executor.submit(self.getting_reports, 1),
                    *[executor.submit(self.get_checked_proxies) for _ in range(self.max_workers_proxies)],
                    *[executor.submit(self.custom_worker) for _ in range(self.max_custom_worker)],
                ]

        except KeyboardInterrupt:
            self.terminate()

        finally:
            while True:
                lst = [future.done() for future in futures_list]
                if not all(lst):
                    time.sleep(1)
                    logger.info(f"Stop {len(list(filter(lambda x: x is False, lst)))} threads. Wait ...")
                else:
                    logger.info("Finish")
                    break

            self.report()
