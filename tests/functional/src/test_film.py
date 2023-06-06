import pytest

from tests.functional.settings import settings


class TestFilms:
    @pytest.mark.asyncio
    async def test_get_all_films(self,
                                 es_write_data,
                                 session_client):
        expected_answer = {'status': 200,
                           'length': 50,
                           'title': 'The Star'}
        url = settings.service_url + '/api/v1/films'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert body[0]['title'] == expected_answer['title']
            assert list(body[0].keys()) == ['uuid', 'title', 'imdb_rating']
            assert type(body[0]['imdb_rating']) == float

    @pytest.mark.asyncio
    async def test_get_all_films_genre(self,
                                       es_write_data,
                                       session_client):
        expected_answer = {'status': 200,
                           'length': 50,
                           'title': 'The Star'}
        url = settings.service_url + '/api/v1/films/?genre=Action'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert body[0]['title'] == expected_answer['title']

        url = settings.service_url + '/api/v1/films/?genre=Music Story'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert body[0]['title'] == expected_answer['title']

        url = settings.service_url + '/api/v1/films/?genre=music'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['length']
            assert body[0]['title'] == expected_answer['title']

    @pytest.mark.asyncio
    async def test_get_all_films_genre_not_exists(self,
                                                  es_write_data,
                                                  session_client):
        expected_answer = {'status': 404,
                           'detail': 'movies not found'}
        url = settings.service_url + '/api/v1/films/?genre=Not Exist'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'] == expected_answer['detail']

    @pytest.mark.asyncio
    async def test_get_all_films_pagination(self,
                                            es_write_data,
                                            session_client):
        expected_answer = {'status': 200,
                           'page_size': 5}
        url = settings.service_url + '/api/v1/films/?page_size=5'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['page_size']

        expected_answer = {'status': 200,
                           'page_size': 60 - 50}
        url = settings.service_url + '/api/v1/films/?page_number=2'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['page_size']

        expected_answer = {'status': 200,
                           'page_size': 5}
        url = settings.service_url + '/api/v1/films/?page_number=4&page_size=5'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert len(body) == expected_answer['page_size']

    @pytest.mark.asyncio
    async def test_get_all_films_pagination_negative(self,
                                                     es_write_data,
                                                     session_client):
        expected_answer = {'status': 422,
                           'type': 'value_error.number.not_ge',
                           'msg': 'greater than or equal to 1'}
        url = settings.service_url + '/api/v1/films/?page_size=-5'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type']
            assert expected_answer['msg'] in body['detail'][0]['msg']

        expected_answer = {'status': 422,
                           'type': 'value_error.number.not_le',
                           'msg': 'less than or equal to 500'}
        url = settings.service_url + '/api/v1/films/?page_size=500000000000000'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type']
            assert expected_answer['msg'] in body['detail'][0]['msg']

        expected_answer = {'status': 422,
                           'type': 'value_error.number.not_ge',
                           'msg': 'greater than or equal to 1'}
        url = settings.service_url + '/api/v1/films/?page_number=-5'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type']
            assert expected_answer['msg'] in body['detail'][0]['msg']

        expected_answer = {'status': 422,
                           'type': 'value_error.number.not_le',
                           'msg': 'less than or equal to 10000'}
        url = settings.service_url + '/api/v1/films/?page_number=5000000000000'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type']
            assert expected_answer['msg'] in body['detail'][0]['msg']