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

        expected_answer = {'status': 422,
                           'type0': 'value_error.number.not_ge',
                           'type1': 'value_error.number.not_le'}
        url = settings.service_url\
            + '/api/v1/films/?page_number=-4&page_size=5000000000'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type0']
            assert body['detail'][1]['type'] == expected_answer['type1']

        expected_answer = {'status': 422,
                           'type0': 'type_error.integer',
                           'type1': 'type_error.integer'}
        url = settings.service_url\
            + '/api/v1/films/?page_number=fff&page_size=pop'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type0']
            assert body['detail'][1]['type'] == expected_answer['type1']

    # Test works ONLY ones because of
    # https://github.com/dkarpele/Async_API_sprint_2/issues/12
    # To make it work again need to remove redis index.
    @pytest.mark.asyncio
    async def test_get_all_films_sort(self,
                                      es_write_data,
                                      session_client):
        expected_answer = {'status': 200,
                           'length': 50,
                           'title': 'The Star'}
        url = settings.service_url + '/api/v1/films/?sort=imdb_rating'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            imdb_rating_list = [i['imdb_rating'] for i in body]
            assert sorted(imdb_rating_list) == imdb_rating_list
            assert imdb_rating_list[0] < imdb_rating_list[len(imdb_rating_list)-1]

        expected_answer = {'status': 200,
                           'length': 50,
                           'title': 'The Star'}
        url = settings.service_url + '/api/v1/films/?sort=-imdb_rating'

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            imdb_rating_list = [i['imdb_rating'] for i in body]
            assert sorted(imdb_rating_list, reverse=True) == imdb_rating_list
            assert imdb_rating_list[0] > imdb_rating_list[
                len(imdb_rating_list) - 1]