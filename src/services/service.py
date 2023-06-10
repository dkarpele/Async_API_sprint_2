import json
from typing import Optional

from redis.asyncio import Redis

from db import AbstractStorage

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class IdRequestService:
    def __init__(self, redis: Redis, storage: AbstractStorage, model):
        self.redis = redis
        self.storage = storage
        self.model = model

    async def get_by_id(self, _id: str, index: str) -> Optional:
        entity = await self._get_from_cache(_id)
        if not entity:
            entity = await self.storage.get_by_id(_id, index, self.model)
            if not entity:
                return None
            await self._put_to_cache(entity)

        return entity

    async def _get_from_cache(self, _id: str) -> Optional:
        data = await self.redis.get(_id)
        if not data:
            return None

        res = self.model.parse_raw(data)
        return res

    async def _put_to_cache(self, entity):
        await self.redis.set(entity.id, entity.json(), CACHE_EXPIRE_IN_SECONDS)


class ListService:
    def __init__(self, redis: Redis, storage: AbstractStorage, model):
        self.redis = redis
        self.storage = storage
        self.model = model

    async def get_list(self,
                       index: str,
                       sort: str = None,
                       search: dict = None,
                       key: str = None,
                       page: int = None,
                       size: int = None) -> Optional:

        if key:
            entities = await self._get_from_cache(key, sort)
        else:
            entities = None
        if not entities:
            entities = await self.storage.get_list(self.model,
                                                   index,
                                                   sort,
                                                   search,
                                                   page,
                                                   size)
            if not entities:
                return None
            if key:
                await self._put_to_cache(key, entities)

        return entities

    async def _get_from_cache(self, name: str = None, sort: str = None) -> Optional:
        data = await self.redis.hgetall(name)
        if not data:
            return None

        res = data.values()
        if sort:
            if sort[0] == '-':
                res = sorted(res, key=lambda x: json.loads(x)[sort[1:]], reverse=True)
            else:
                res = sorted(res, key=lambda x: json.loads(x)[sort])
        return [self.model.parse_raw(i) for i in res]

    async def _put_to_cache(self, key: str, entities: list):
        entities_dict: dict = \
            {item: entity.json() for item, entity in enumerate(entities)}
        await self.redis.hset(name=key, mapping=entities_dict)
        await self.redis.expire(name=key, time=CACHE_EXPIRE_IN_SECONDS)
