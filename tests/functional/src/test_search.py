import datetime
import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk, BulkIndexError

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_search(add_films, http_client):
    url = test_settings.service_url + '/api/v1/films'
    query_data = {'search': 'The Star'}
    async with http_client.get(url, params=query_data) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    assert status == 200
    assert len(body) == 50