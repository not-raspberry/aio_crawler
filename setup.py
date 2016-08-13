#!/usr/bin/env python3
"""aio_crawler project setup."""
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
    'aiohttp==0.22.5',
    'click==6.6',
]

TEST_REQUIREMENTS = [
    'pylama==7.0.9',
    'pytest==2.9.2',
]

setup(
    name='aio_crawler',
    version='0.0.1',
    description='AIO website crawler',
    long_description=README,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='aio crawler web spider',
    author='Michał Pawłowski',
    author_email='@'.join(['unittestablecode', 'gmail.com']),
    license='MIT',
    packages=find_packages(exclude=['test']),
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    extras_require={'tests': TEST_REQUIREMENTS},
    cmdclass={},
    entry_points={
    },
)
