"""Command-line interface."""
import sys
import json
import logging
import click
from aio_crawler.crawler import Crawler


@click.command()
@click.option('-c', '--concurrency', type=int, default=20, help='Number of parallel downloads.')
@click.option('-t', '--timeout', type=float, default=10.0, help='Timeout of each single request.')
@click.option('-v', '--verbose', count=True)
@click.argument('site-address')
def cli_entry(site_address, timeout, concurrency, verbose):
    """Crawl the website and print results to stdout."""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    crawler = Crawler(site_address, timeout, concurrency)
    results = crawler.crawl()
    json.dump(results, sys.stdout, indent=4, ensure_ascii=False)
