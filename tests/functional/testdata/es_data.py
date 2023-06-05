import uuid


def get_es_data():
    movies = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [
            {'id': '11', 'name': 'Action'},
            {'id': '22', 'name': 'Sci'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'directors': [
            {'id': '111', 'name': 'Georg'},
            {'id': '222', 'name': 'Lucas'}
        ],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'film_work_type': 'movie'
    } for _ in range(60)]

    return movies

