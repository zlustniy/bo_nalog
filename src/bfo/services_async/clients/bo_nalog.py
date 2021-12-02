import json
import logging
import tempfile
from typing import Tuple
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientResponse, ClientResponseError
from django.conf import settings

from project.services.aiohttp_tool import AIOHTTPDefaultKwargs

bonalog_logger = logging.getLogger('bo_nalog_client')


class BoNalogClient:
    CHUNK_SIZE = 1028

    def __init__(self) -> None:
        self.host = settings.BONALOG_HOST

    def _make_url(self, path) -> str:
        return urljoin(self.host, path)

    async def get_nbo_organizations_search(self, ogrn) -> dict:
        async with aiohttp.ClientSession() as session:
            url = self._make_url(
                path=f'/nbo/organizations/search?query={ogrn}&page=0',
            )
            async with session.get(
                    url=url,
                    **AIOHTTPDefaultKwargs(url=url).get(),
            ) as response:
                try:
                    response.raise_for_status()
                except (json.JSONDecodeError, ClientResponseError) as e:
                    bonalog_logger.exception('get_nbo_organizations_search error: %s', e)
                    raise e
                return await response.json()

    async def download_file_bfo(self, file_id, period) -> Tuple[ClientResponse, bytes]:
        async with aiohttp.ClientSession() as session:
            url = self._make_url(
                path=f'/download/bfo/pdf/{file_id}?period={period}',
            )
            async with session.get(
                    url=url,
                    **AIOHTTPDefaultKwargs(url=url).get(),
            ) as response:
                with tempfile.NamedTemporaryFile(suffix=f'_{file_id}') as temporary_file:
                    async for chunk in response.content.iter_chunked(1024 * 5):
                        temporary_file.write(chunk)
                    temporary_file.seek(0)
                    response_content = temporary_file.read()
                    return response, response_content
