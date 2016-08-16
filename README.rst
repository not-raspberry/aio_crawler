aio_crawler |status|
====================

.. |status| image:: https://travis-ci.org/not-raspberry/aio_crawler.svg?branch=master
    :target: https://travis-ci.org/not-raspberry/aio_crawler

Single site web crawler using aiohttp.

Usage
-----

Install from source::

    ./setup.py install

.. code::

    $ aio_crawler --help
    Usage: aio_crawler [OPTIONS] SITE_ADDRESS

    Crawl the website and print results to stdout.

    Options:
    -c, --concurrency INTEGER  Number of parallel downloads.
    -t, --timeout FLOAT        Timeout of each single request.
    -v, --verbose
    --help                     Show this message and exit.


Development
-----------

It's strongly advised to use a virtualenv.

Install dependencies and the CLI hook::

    ./setup.py develop


Install test dependencies::

    pip install -e '.[tests]'


System requirements
-------------------

Python 3.5.

If your OS does not ship Python 3.5, use pyenv_. It's miserable but better than nothing.

.. _pyenv: https://github.com/yyuu/pyenv
