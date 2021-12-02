from functools import cached_property
from urllib.parse import urlparse

import aiohttp

from project.services.proxies import Proxies
from project.services.user_agent import RandomUserAgent


class AIOHTTPDefaultKwargs:
    def __init__(self, url: str):
        self.url = url

    @cached_property
    def url_scheme(self) -> str:
        parse_result = urlparse(self.url)
        return parse_result.scheme

    @cached_property
    def proxy(self) -> str:
        proxies = Proxies.get()
        proxy_for_url = proxies.get(self.url_scheme)
        return proxy_for_url

    @staticmethod
    def _get_default_headers() -> dict:
        return {
            'User-Agent': RandomUserAgent().get(),
        }

    def get(self, extra_headers: dict | None = None, timeout: float = 20) -> dict:
        if extra_headers is None:
            extra_headers = {}
        headers = self._get_default_headers()
        headers.update(**extra_headers)

        kwargs = {
            'headers': headers,
            'timeout': aiohttp.ClientTimeout(total=timeout),
        }

        if self.proxy:
            kwargs.update({
                'proxy': self.proxy,
            })

        return kwargs
