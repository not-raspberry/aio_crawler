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


async def fetching_worker(session, queue, url_to_results):
    """Repeatedly run the fetching corouting and update visited URLs."""
    while True:
        address = await queue.get()
        url_to_results[address] = None
        log.debug('Visiting %s', address)

        try:
            with aiohttp.Timeout(TIMEOUT):
                links, resources = await fetch_page(session, address)
        except asyncio.TimeoutError as e:
            log.warning('Timed out, requeueing the resource: %s', address)
            queue.put_nowait(address)
            continue

        url_to_results[address] = (links, resources)

        for url in links:
            if url not in url_to_results:
                queue.put_nowait(url)
            url_to_results.setdefault(None)
        queue.task_done()


def crawl(starting_address, concurrency=20):
    """Crawl the entire website."""
    loop = asyncio.get_event_loop()
    url_to_results = {}
    queue = asyncio.Queue()
    queue.put_nowait(starting_address)

    with aiohttp.ClientSession(loop=loop) as session:
        tasks = [loop.create_task(fetching_worker(session, queue, url_to_results))
                 for _ in range(concurrency)]

        try:
            loop.run_until_complete(queue.join())
        except KeyboardInterrupt:
            log.warning('Keyboard interrupt. Will return partial results.')
            raise
        finally:
            for task in tasks:
                task.cancel()
            loop.run_until_complete(asyncio.wait(tasks))
            return url_to_results
