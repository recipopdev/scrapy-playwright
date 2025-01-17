#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='scrapy-puppeteer-client',
    version='0.0.7',
    description='A library to use Playwright-managed browser in Scrapy spiders',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/recipopdev/scrapy-playwright/',
    author='MODIS @ ISP RAS',
    maintainer='Adimo',
    maintainer_email='mohammed@adimo.co',
    packages=['scrapypuppeteer'],
    requires=['scrapy'],
    python_requires='>=3.5',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Scrapy',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License'
    ]
)
