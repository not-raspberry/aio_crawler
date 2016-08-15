"""Crawling logic."""
import logging
from asyncio import get_event_loop, wait, Task, TimeoutError
import aiohttp

from .reader import resources_from_tag_soup


log = logging.getLogger(__name__)


async def fetch_page(session: aiohttp.ClientSession, url: str) -> tuple:
    """
    Grab a page and return a tuple of lists of links and resources.

    :return: tuple of sets of links and all resources, including links
    """
    async with session.get(url) as response:
        if not 200 <= response.status < 300:
            log.warning('Non-OK response (%s) received at %s', response.status, url)
            return (set(), set())

        if 'html' not in response.headers['content-type']:
            return (set(), set())

        html = await response.text()
        links, resources = resources_from_tag_soup(html, url)
        return links, resources


class Crawler():
    """A crawler implemantation, mapping links and other resources of a single site."""

    def __init__(self, address: str, timeout: float = 10.0):
        """Initialize the crawler."""
        self.url_to_results = {}
        self.address = address
        self.timeout = timeout
        self.loop = get_event_loop()

    async def fetching_worker(self, address: str, session: aiohttp.ClientSession):
        """
        Grab the page, discover links and run coroutines to fetch them.

        Coroutines for grabbing resources are opened eagerly. They don't start
        all at once anyway because the `session` has its internal pool.

        At the end of the coroutine we check if the current coroutine is the last
        remaining one on the event loop. If so, that means no other links are left
        to consume.
        """
        log.info('Visiting %s', address)

        try:
            with aiohttp.Timeout(self.timeout):
                links, resources = await fetch_page(session, address)
        except TimeoutError as e:
            log.warning('Timed out, requeueing the resource: %s', address)
            self.loop.create_task(self.fetching_worker(address, session))

        self.url_to_results[address] = (links, resources)

        for url in links:
            # Eagerly creating coroutines for unseen links.
            if url not in self.url_to_results:
                self.url_to_results[address] = None  # Marking links as seen.
                self.loop.create_task(self.fetching_worker(url, session))

        if Task.all_tasks() == {Task.current_task()}:
            # No other resources to grab.
            self.loop.stop()

    def crawl(self, concurrency: int = 20) -> dict:
        """
        Crawl the entire website.

        :return: A dict with crawling results.
        """
        connector = aiohttp.TCPConnector(limit=concurrency)
        with aiohttp.ClientSession(loop=self.loop, connector=connector) as session:
            self.loop.create_task(self.fetching_worker(self.address, session))
            try:
                self.loop.run_forever()
            except KeyboardInterrupt:
                log.warning('Keyboard interrupt. Will return partial results.')
                tasks = Task.all_tasks()
                for task in tasks:
                    task.cancel()
                self.loop.run_until_complete(wait(tasks))
            finally:
                return self.url_to_results
