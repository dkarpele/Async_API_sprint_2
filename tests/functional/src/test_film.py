import pytest

from tests.functional.settings import settings

expected_answer = {'status': 200,
                   'length': 50,
                   'search': 'The Star'}


@pytest.mark.asyncio
async def test_film(es_write_data,
                    session_client):
    url = settings.service_url + '/api/v1/films'

    async with session_client.get(url) as response:
        body = await response.json()
        assert response.status == expected_answer['status']
        assert len(body) == expected_answer['length']
        assert body[0]['title'] == expected_answer['search']
