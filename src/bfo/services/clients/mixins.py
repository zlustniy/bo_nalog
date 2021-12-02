import redis_lock
import requests.utils
from django.core.cache import cache
from django_redis import get_redis_connection
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from project.services.proxies import Proxies
from project.services.user_agent import RandomUserAgent

requests.packages.urllib3.disable_warnings()  # Disable InsecureRequestWarning
requests.utils.default_user_agent = lambda: RandomUserAgent().get()


class AuthTokenMixin:
    cache_access_token_key = None
    cache_timeout = None
    expire: int = 10
    _lock: redis_lock.Lock

    def __init__(self):
        redis_client = get_redis_connection()
        self._lock = redis_lock.Lock(redis_client, 'token_lock_cache', expire=self.expire, auto_renewal=True)

    def get_access_token(self):
        raise NotImplementedError

    def get_access_token_with_cache(self):
        with self._lock:
            access_token = self.get_cache_token()
            if access_token:
                return access_token
            access_token = self.get_access_token()
            self.set_cache_token(access_token)
            return access_token

    def set_cache_token(self, access_token):
        cache.set(self.cache_access_token_key, access_token, timeout=self.cache_timeout)

    def get_cache_token(self):
        return cache.get(self.cache_access_token_key)

    def clear_cache_token(self):
        cache.delete(self.cache_access_token_key)


class MakeRetrySessionMixin:
    total_retries = 5
    backoff_factor = 0.1
    status_forcelist = [500, 502, 503, 504]
    retry_session = None

    def make_retry_session(self):
        self.retry_session = self._requests_retry_session()

    def _requests_retry_session(self):
        session = Session()
        session.proxies.update(Proxies.get())

        retry = Retry(
            total=self.total_retries,
            backoff_factor=self.backoff_factor,  # sleep time = [0.0; 0.2; 0.4; 0.8; 1.6;] (for 0.1)
            status_forcelist=self.status_forcelist,
            method_whitelist=['GET', 'POST'],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def retry_get(self, url, **kwargs):
        return self.retry_session.get(url=url, **kwargs)

    def retry_post(self, url, data=None, json=None, **kwargs):
        return self.retry_session.post(url=url, data=data, json=json, **kwargs)
