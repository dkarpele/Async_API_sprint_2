from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError, RequestError
from redis.asyncio import Redis

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
ES_MAX_SIZE = 50


class IdRequestService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, model):
        self.redis = redis
        self.elastic = elastic
        self.model = model

    async def get_by_id(self, _id: str, index: str) -> Optional:
        entity = await self._get_from_cache(_id)
        if not entity:
            entity = await self._get_from_elastic(_id, index)
            if not entity:
                return None
            await self._put_to_cache(entity)

        return entity

    async def _get_from_elastic(self, _id: str, index: str) -> Optional:
        try:
            doc = await self.elastic.get(index=index, id=_id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])

    async def _get_from_cache(self, _id: str) -> Optional:
        data = await self.redis.get(_id)
        if not data:
            return None

        res = self.model.parse_raw(data)
        return res

    async def _put_to_cache(self, entity):
        await self.redis.set(entity.id, entity.json(), CACHE_EXPIRE_IN_SECONDS)


class ListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, model):
        self.redis = redis
        self.elastic = elastic
        self.model = model

    async def get_list(self,
                       index: str,
                       sort: str = None,
                       search: dict = None,
                       key: str = None,
                       page: int = None,
                       size: int = None) -> Optional:

        if key:
            entities = await self._get_from_cache(key)
        else:
            entities = None
        if not entities:
            entities = await self._get_from_elastic(index,
                                                    sort,
                                                    search,
                                                    page,
                                                    size)
            if not entities:
                return None
            if key:
                await self._put_to_cache(key, entities)

        return entities

    async def _get_from_elastic(self,
                                index: str,
                                sort: str = None,
                                search: dict = None,
                                page: int = None,
                                size: int = None) -> Optional:
        if sort:
            try:
                order = 'desc' if sort.startswith('-') else 'asc'
                sort = sort[1:] if sort.startswith('-') else sort
                sorting = [{sort: {'order': order}}]
            except AttributeError:
                sorting = None
        else:
            sorting = None

        if page and size:
            offset = (page * size) - size
        elif page and not size:
            size = ES_MAX_SIZE
            offset = (page * size) - size
        elif not page and size:
            offset = None
        else:
            offset = None
            size = ES_MAX_SIZE

        try:
            docs = await self.elastic.search(
                index=index,
                query=search,
                size=size,
                sort=sorting,
                from_=offset
            )
        except (NotFoundError, RequestError):
            return None

        return [self.model(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_from_cache(self, name: str = None) -> Optional:
        data = await self.redis.hgetall(name)
        if not data:
            return None

        res = [self.model.parse_raw(i) for i in data.values()]
        return res

    async def _put_to_cache(self, key: str, entities: list):
        entities_dict: dict =\
            {item: entity.json() for item, entity in enumerate(entities)}
        await self.redis.hset(name=key, mapping=entities_dict)
        await self.redis.expire(name=key, time=CACHE_EXPIRE_IN_SECONDS)
