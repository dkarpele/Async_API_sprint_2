import pytest

from tests.functional.settings import settings

PREFIX = '/api/v1/films'


@pytest.mark.usefixtures('es_write_data')
class TestFilms:
    @pytest.mark.parametrize(
        'url, expected_answer',
        [
            (
                    f'{PREFIX}',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?genre=Action',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?genre=Music Story',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?genre=music',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?page_size=5',
                    {'status': 200, 'length': 5, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?page_number=2',
                    {'status': 200, 'length': 60 - 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?page_number=4&page_size=5',
                    {'status': 200, 'length': 5, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?page_number=4&page_size=5&genre=Action',
                    {'status': 200, 'length': 5, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/?genre=doesntexist',
                    {'status': 404, 'detail': 'movies not found'}
            ),
            (
                    f'{PREFIX}/?page_number=4&page_size=5&genre=doesntexist',
                    {'status': 404, 'detail': 'movies not found'}
            ),
        ]
    )
    @pytest.mark.asyncio
    async def test_get_all_films(self,
                                 session_client,
                                 url,
                                 expected_answer):
        url = settings.service_url + url

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            if 'doesntexist' in url:
                assert body['detail'] == 'movies not found'
            else:
                assert len(body) == expected_answer['length']
                assert body[0]['title'] == expected_answer['title']
                assert list(body[0].keys()) == ['uuid', 'title', 'imdb_rating']
                assert type(body[0]['imdb_rating']) == float

    @pytest.mark.parametrize(
        'url, expected_answer',
        [
            (
                f'{PREFIX}/?page_size=-5',
                {'status': 422,
                 'type0': 'value_error.number.not_ge',
                 'msg': 'greater than or equal to 1'}
            ),
            (
                f'{PREFIX}/?page_size=500000000000000',
                {'status': 422,
                 'type0': 'value_error.number.not_le',
                 'msg': 'less than or equal to 500'}
            ),
            (
                f'{PREFIX}/?page_number=-5',
                {'status': 422,
                 'type0': 'value_error.number.not_ge',
                 'msg': 'greater than or equal to 1'}
            ),
            (
                f'{PREFIX}/?page_number=5000000000000&genre=Action',
                {'status': 422,
                 'type0': 'value_error.number.not_le',
                 'msg': 'less than or equal to 10000'}
            ),
            (
                f'{PREFIX}/?page_number=-4&page_size=5000000000',
                {'status': 422,
                 'type0': 'value_error.number.not_ge',
                 'msg': 'greater than or equal to 1',
                 'type1': 'value_error.number.not_le'}
            ),
            (
                f'{PREFIX}/?page_number=fff&page_size=pop',
                {'status': 422,
                 'type0': 'type_error.integer',
                 'msg': 'value is not a valid integer',
                 'type1': 'type_error.integer'}
            )
        ]
    )
    @pytest.mark.asyncio
    async def test_get_all_films_pagination_negative(self,
                                                     session_client,
                                                     url,
                                                     expected_answer):
        url = settings.service_url + url

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'][0]['type'] == expected_answer['type0']
            assert expected_answer['msg'] in body['detail'][0]['msg']
            try:
                assert body['detail'][1]['type'] == expected_answer['type1']
            except (KeyError, IndexError):
                pass

    # Test works ONLY ONES because of
    # https://github.com/dkarpele/Async_API_sprint_2/issues/12
    # To make it work again need to remove redis index.
    # $ docker exec -ti redis bash
    # root@c8e62cb99f32:/data# redis-cli FLUSHALL
    @pytest.mark.parametrize(
        'url, expected_answer, reverse',
        [
            (
                f'{PREFIX}/?sort=imdb_rating',
                {'status': 200},
                False
            ),
            (
                f'{PREFIX}/?sort=-imdb_rating',
                {'status': 200},
                True
            ),
            (
                f'{PREFIX}/search?query=Star&sort=-imdb_rating',
                {'status': 200},
                True
            ),
            (
                f'{PREFIX}/?sort=doesntexist',
                {'status': 404},
                True
            ),
            (
                f'{PREFIX}/search?query=doesntexist&sort=imdb_rating',
                {'status': 404},
                True
            )
        ]
    )
    @pytest.mark.asyncio
    async def test_get_all_films_sort(self,
                                      session_client,
                                      url,
                                      expected_answer,
                                      reverse):
        url = settings.service_url + url

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            if 'doesntexist' in url:
                assert body['detail'] == 'movies not found'
            else:
                imdb_rating_list = [i['imdb_rating'] for i in body]
                assert sorted(imdb_rating_list, reverse=reverse) == \
                       imdb_rating_list
                if not reverse:
                    assert imdb_rating_list[0] < \
                        imdb_rating_list[len(imdb_rating_list) - 1]
                else:
                    assert imdb_rating_list[0] > \
                        imdb_rating_list[len(imdb_rating_list) - 1]

        # TODO: This is w/a. Need to remove after fix of #12. See comment above
        import redis
        redis_cli = redis.Redis(host=settings.redis_host,
                                port=settings.redis_port)
        redis_cli.flushall()


@pytest.mark.usefixtures('es_write_data')
class TestFilmID:
    @pytest.mark.asyncio
    async def test_get_film_by_id(self,
                                  session_client,
                                  get_film_id):
        _id = get_film_id
        expected_answer = {'status': 200, 'length': 8, 'title': 'The Star'}
        url = settings.service_url + PREFIX + '/' + _id

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['title'] == expected_answer['title']
            assert len(body) == expected_answer['length']
            assert body['uuid'] == _id
            assert list(body.keys()) == ['uuid', 'title', 'imdb_rating',
                                         'description', 'genre', 'actors',
                                         'writers', 'directors']

    @pytest.mark.asyncio
    async def test_get_film_id_not_exists(self,
                                          session_client):

        url = settings.service_url + PREFIX + '/' + 'BAD_ID'
        expected_answer = {'status': 404}
        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            assert body['detail'] == "BAD_ID not found in movies"


@pytest.mark.usefixtures('es_write_data')
class TestFilmSearch:
    @pytest.mark.parametrize(
        'url, expected_answer',
        [
            (
                    f'{PREFIX}/search?query=Star',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/search?query=The Star',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/search?query=star',
                    {'status': 200, 'length': 50, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/search?query=Star&page_number=4&page_size=5',
                    {'status': 200, 'length': 5, 'title': 'The Star'}
            ),
            (
                    f'{PREFIX}/search?query=Star&page_number=4&page_size=5000',
                    {'status': 422,
                     'type0': 'value_error.number.not_le',
                     'msg': 'less than or equal to 500'}
            ),
            (
                    f'{PREFIX}/search?query=doesntexist',
                    {'status': 404, 'detail': 'movies not found'}
            ),
            (
                    f'{PREFIX}/search?query=',
                    {'status': 404, 'detail': 'Empty `query` attribute'}
            ),
        ]
    )
    @pytest.mark.asyncio
    async def test_search_films(self,
                                session_client,
                                url,
                                expected_answer):
        url = settings.service_url + url

        async with session_client.get(url) as response:
            body = await response.json()
            assert response.status == expected_answer['status']
            if 'doesntexist' in url or url.endswith('='):
                assert body['detail'] == expected_answer['detail']
            elif 'page_size=5000' in url:
                assert body['detail'][0]['type'] == expected_answer['type0']
                assert expected_answer['msg'] in body['detail'][0]['msg']
            else:
                assert len(body) == expected_answer['length']
                assert body[0]['title'] == expected_answer['title']
                assert list(body[0].keys()) == ['uuid', 'title', 'imdb_rating']
                assert type(body[0]['imdb_rating']) == float
