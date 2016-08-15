"""Crawling logic."""
import logging
import asyncio
import aiohttp

from .reader import resources_from_tag_soup


TIMEOUT = 10  # sec

log = logging.getLogger(__name__)


async def fetch_page(session, url):
    """Grab a page and return a tuple of lists of links and resources."""
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

    def __init__(self, address):
        """Initialize the crawler."""
        self.address = address
        self.url_to_results = {}
        self.queue = asyncio.Queue()

    async def fetching_worker(self, session):
        """Repeatedly run the fetching coroutine and update visited URLs."""
        while True:
            address = await self.queue.get()
            self.url_to_results[address] = None
            log.debug('Visiting %s', address)

            try:
                with aiohttp.Timeout(TIMEOUT):
                    links, resources = await fetch_page(session, address)
            except asyncio.TimeoutError as e:
                log.warning('Timed out, requeueing the resource: %s', address)
                self.queue.put_nowait(address)
                continue

            self.url_to_results[address] = (links, resources)

            for url in links:
                if url not in self.url_to_results:
                    self.queue.put_nowait(url)
                self.url_to_results.setdefault(None)
            self.queue.task_done()

    def crawl(self, concurrency=20):
        """Crawl the entire website."""
        loop = asyncio.get_event_loop()
        self.queue.put_nowait(self.address)

        with aiohttp.ClientSession(loop=loop) as session:
            tasks = [loop.create_task(self.fetching_worker(session))
                     for _ in range(concurrency)]

            try:
                loop.run_until_complete(self.queue.join())
            except KeyboardInterrupt:
                log.warning('Keyboard interrupt. Will return partial results.')
                raise
            finally:
                for task in tasks:
                    task.cancel()
                loop.run_until_complete(asyncio.wait(tasks))

                return self.url_to_results
