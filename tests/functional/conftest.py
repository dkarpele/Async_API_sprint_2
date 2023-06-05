import aiohttp
import asyncio
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import settings
from tests.functional.testdata import es_data


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=f'{settings.elastic_host}:{settings.elastic_port}')
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session')
async def session_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def es_write_data(es_client):
    def get_es_bulk_query(data):
        doc = []
        for row in data:
            doc.append(
                {'_index': settings.es_index,
                 '_id': row[settings.es_id_field],
                 '_source': row
                 })
        return doc

    bulk_query = get_es_bulk_query(es_data.get_es_data())

    await async_bulk(es_client, bulk_query)
    await es_client.indices.refresh()

    yield

    await es_client.indices.delete(index=settings.es_index)
