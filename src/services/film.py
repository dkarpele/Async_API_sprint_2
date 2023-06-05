from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.films import Film
from services.service import IdRequestService, ListService


# get_film_service — это провайдер IdRequestService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db.
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином
# экземпляре (синглтона)
@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)) -> IdRequestService:
    return IdRequestService(redis, elastic, Film)


@lru_cache()
def get_film_list_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)) -> ListService:
    return ListService(redis, elastic, Film)
