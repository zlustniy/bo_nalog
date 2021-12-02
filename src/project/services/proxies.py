from django.conf import settings


class Proxies:
    @staticmethod
    def get() -> dict:
        proxies = {}
        if settings.HTTP_DOWNLOAD_PROXY is not None:
            key = 'http'
            proxies.update({
                key: settings.HTTP_DOWNLOAD_PROXY,
            })
        if settings.HTTPS_DOWNLOAD_PROXY is not None:
            key = 'https'
            proxies.update({
                key: settings.HTTPS_DOWNLOAD_PROXY,
            })
        return proxies
