import json
from collections import defaultdict
from urllib.parse import urljoin, urlencode

from scrapy import Request, signals
from scrapy.crawler import Crawler
from scrapy.http import Headers, TextResponse

from scrapypuppeteer import PuppeteerRequest, PuppeteerResponse


class PuppeteerServiceDownloaderMiddleware:
    def __init__(self, crawler: Crawler, service_url: str):
        self.service_base_url = service_url
        self.crawler = crawler
        self.used_contexts = defaultdict(set)

    @classmethod
    def from_crawler(cls, crawler):
        service_url = crawler.settings.get('PUPPETEER_SERVICE_URL')
        if service_url is None:
            raise ValueError('Puppeteer service URL must be provided')
        middleware = cls(crawler, service_url)
        crawler.signals.connect(middleware.close_used_contexts,
                                signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        if not isinstance(request, PuppeteerRequest):
            return

        action = request.action
        service_url = urljoin(self.service_base_url, action.endpoint)
        service_params = self._encode_service_params(request)
        if service_params:
            service_url += '?' + service_params
        return request.replace(
            cls=Request,
            url=service_url,
            method='POST',
            headers=Headers({'Content-Type': action.content_type}),
            body=action.serialize_body(),
            dont_filter=True,
            meta={
                'puppeteer_request': request,
                'dont_obey_robotstxt': True
            }
        )

    @staticmethod
    def _encode_service_params(request):
        service_params = {}
        if request.context_id is not None:
            service_params['contextId'] = request.context_id
        if request.page_id is not None:
            service_params['pageId'] = request.page_id
        if request.close_page:
            service_params['closePage'] = 1
        return urlencode(service_params)

    def process_response(self, request, response, spider):
        if not isinstance(response, TextResponse):
            return response

        puppeteer_request = request.meta.get('puppeteer_request')
        if puppeteer_request is None:
            return response

        response_data = json.loads(response.text)
        response = PuppeteerResponse(
            url=puppeteer_request.url,
            body=response_data.get('html'),
            encoding='utf-8',
            puppeteer_request=puppeteer_request,
            context_id=response_data.get('contextId'),
            page_id=response_data.get('pageId')
        )

        self.used_contexts[id(spider)].add(response_data.get('contextId'))

        return response

    def close_used_contexts(self, spider):
        contexts = list(self.used_contexts[id(spider)])
        if contexts:
            request = Request(urljoin(self.service_base_url, '/close_context'),
                              method='POST',
                              headers=Headers({'Content-Type': 'application/json'}),
                              body=json.dumps(contexts))
            return self.crawler.engine.downloader.fetch(request, None)
