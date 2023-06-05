import logging
import time

from redis.asyncio import Redis
from logging import config as logging_config

from utils.logger import LOGGING
from settings import settings


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


async def wait_redis():
    redis_client = Redis(host=settings.redis_host,
                         port=settings.redis_port,
                         ssl=False)
    while True:
        if redis_client.ping():
            logging.info(f"Redis replied successfully on "
                         f"http://{settings.redis_host}:"
                         f"{settings.redis_port}")
            break
        time.sleep(1)
