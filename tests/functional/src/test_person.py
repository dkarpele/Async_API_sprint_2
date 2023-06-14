import logging

import pytest
from logging import config as logging_config

from tests.functional.settings import settings
from tests.functional.utils.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

PREFIX = '/api/v1/persons'


@pytest.mark.usefixtures('redis_clear_data_before_after', 'es_write_data')
class TestPersonID:
    @pytest.mark.asyncio
    async def test_get_person_by_id(self,
                                    session_client,
                                    get_id):
        _id = await get_id(f'{PREFIX}/search?query=Jack&page_number=1&page_size=1')
        expected_answer = {'status': 200, 'length': 3, 'full_name': 'Jack Jones'}
        url = settings.service_url + PREFIX + '/' + _id

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['full_name'] == expected_answer['full_name']
            assert len(body) == expected_answer['length']
            assert body['uuid'] == _id
            assert list(body.keys()) == ['uuid', 'full_name', 'films']
            assert len(body['films']) == 50
            assert list(body['films'][0].keys()) == ['uuid', 'roles']

    @pytest.mark.asyncio
    async def test_get_person_id_not_exists(self,
                                            session_client):
        url = settings.service_url + PREFIX + '/' + 'BAD_ID'
        expected_answer = {'status': 404}
        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'] == "BAD_ID not found in persons"

    @pytest.mark.asyncio
    async def test_get_persons_films_by_id(self,
                                           session_client,
                                           get_id):
        _id = await get_id(f'{PREFIX}/search?query=Jack&page_number=1&page_size=1')
        expected_answer = {'status': 200, 'length': 50}
        url = settings.service_url + PREFIX + '/' + _id + '/film'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert list(body[0].keys()) == ['uuid', 'title', 'imdb_rating']


@pytest.mark.usefixtures('redis_clear_data_before_after', 'es_write_data')
class TestPersonSearch:
    @pytest.mark.parametrize(
        'url, expected_answer',
        [
            (
                    f'{PREFIX}/search?query=Jack',
                    {'status': 200, 'length': 1, 'full_name': 'Jack Jones', 'len_films': 50}
            ),
            (
                    f'{PREFIX}/search?query=Jack',
                    {'status': 200, 'length': 1, 'full_name': 'Jack Jones', 'len_films': 50}
            ),
            (
                    f'{PREFIX}/search?query=jack',
                    {'status': 200, 'length': 1, 'full_name': 'Jack Jones', 'len_films': 50}
            ),
        ]
    )
    @pytest.mark.asyncio
    async def test_search_persons(self,
                                  session_client,
                                  url,
                                  expected_answer):
        url = settings.service_url + url

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert body[0]['full_name'] == expected_answer['full_name']
            assert list(body[0].keys()) == ['uuid', 'full_name', 'films']
            assert type(body[0]['films']) == list
            assert len(body[0]['films']) == expected_answer['len_films']

    @pytest.mark.asyncio
    async def test_search_persons_pagination_negative(self,
                                                      session_client):
        url = settings.service_url + \
              f'{PREFIX}/search?query=Jack&page_number=4&page_size=5000'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == 422
            assert body['detail'][0]['type'] == 'value_error.number.not_le'
            assert 'less than or equal to 500' in body['detail'][0]['msg']

    @pytest.mark.parametrize(
        'url, expected_answer',
        [
            (
                    f'{PREFIX}/search?query=doesntexist',
                    {'status': 404, 'detail': 'persons not found'}
            ),
            (
                    f'{PREFIX}/search?query=Jack&page_number=4&page_size=4',
                    {'status': 404, 'detail': 'persons not found'}
            ),
            (
                    f'{PREFIX}/search?query=',
                    {'status': 404, 'detail': 'Empty `query` attribute'}
            ),
        ]
    )
    @pytest.mark.asyncio
    async def test_search_persons_not_found(self,
                                            session_client,
                                            url,
                                            expected_answer):
        url = settings.service_url + url

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'] == expected_answer['detail']


class TestPersonIdRedis:
    """
    The idea behind the Test class is:
    1. Run method `prepare`, that will load data to ES:
        1. Run HTTP request that will load data to redis
        2. Remove all data from ES
    2. Run method `get_from_redis`:
        1. Run HTTP request that will try to get data from redis
        2. Show the output
        3. Upload the data to redis
    """

    # This test only adds data to ES, adds data to redis, removes data from ES
    @pytest.mark.asyncio
    async def test_prepare_data(self,
                                redis_clear_data_before,
                                es_write_data,
                                session_client,
                                get_id):
        # Collect film uuid
        global _id
        _id = await get_id(f'{PREFIX}/search?query=Jack&page_size=1')

        # Find data by id
        url = settings.service_url + PREFIX + '/' + _id
        async with session_client.get(url) as response:
            assert response.status == 200

    # This test DOESN'T add data to ES, but adds data to redis
    @pytest.mark.asyncio
    async def test_get_from_redis(self,
                                  redis_clear_data_after,
                                  session_client):

        expected_answer = {'status': 200, 'length': 3, 'full_name': 'Jack Jones'}
        try:
            url = settings.service_url + PREFIX + '/' + _id
        except NameError:
            logging.error("Can't run the test /persons/UUID with unknown id")
            assert False

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['full_name'] == expected_answer['full_name']
            assert len(body) == expected_answer['length']
            assert body['uuid'] == _id
            assert list(body.keys()) == ['uuid', 'full_name', 'films']

    @pytest.mark.asyncio
    async def test_get_films_from_redis(self,
                                        redis_clear_data_after,
                                        session_client):
        expected_answer = {'status': 200, 'length': 50}
        try:
            url = settings.service_url + PREFIX + '/' + _id + '/film'
        except NameError:
            logging.error("Can't run the test /persons/UUID with unknown id")
            assert False

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert list(body[0].keys()) == ['uuid', 'title', 'imdb_rating']
