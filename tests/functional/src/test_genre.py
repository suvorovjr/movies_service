import datetime
import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from elasticsearch.helpers import async_bulk

from ..settings import test_settings
from ..fixtures.es_data import GENRE_UUID, GENRE_NAME
from ..testdata.indexes import indexes, Genre


@pytest.mark.parametrize(
    'index, status_code',
    [
        (
            "/movies",
            200,
        ),
        (
            "/genres",
            200,
        ),
        (
            "/persons",
            200,
        )
    ]
)
@pytest.mark.asyncio
async def test_index_is_create(
    create_es_indexes,
    http_client: aiohttp.ClientSession,
    index,
    status_code
):
    async with http_client.get(f"{test_settings.es_url_to_connect}{index}") as response:
        assert response.status == status_code

@pytest.mark.skip
@pytest.mark.asyncio
async def test_get_genre(
    add_genre,
    http_client: aiohttp.ClientSession
):
    async with http_client.get(
        f"http://{test_settings.service_url}/api/v1/genres/{GENRE_UUID}/"
    ) as response:
        assert response.status == 200
        result = response.json()
        assert result.get("name") == GENRE_NAME

@pytest.mark.skip
@pytest.mark.asyncio
async def test_get_genre_list(
    add_genres,
    http_client: aiohttp.ClientSession
):
    async with http_client.get(
        f"http://{test_settings.service_url}/api/v1/genres/"
    ) as response:
        assert response.status == 200


