import logging
import time

from elasticsearch import Elasticsearch
from logging import config as logging_config

from utils.logger import LOGGING
from settings import settings

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


async def wait_es():
    print(settings.elastic_host)
    es_client = Elasticsearch(
        hosts=f'http://{settings.elastic_host}:{settings.elastic_port}',
        validate_cert=False,
        use_ssl=False)
    while True:
        if es_client.ping(human=True, pretty=True):
            logging.info(f"ES replied successfully on "
                         f"http://{settings.elastic_host}:"
                         f"{settings.elastic_port}")
            break
        time.sleep(1)
