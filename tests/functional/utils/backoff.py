import logging
from functools import wraps
from time import sleep
from redis.exceptions import ConnectionError


class BackoffError(Exception):
    ...


def backoff(servise, start_sleep_time=0.1, factor=2, border_sleep_time=900):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный
    экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param logger: логирование функций
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            new_factor = factor
            while True:
                try:
                    await func(*args, **kwargs)
                    logging.info(f"Подключение к {servise} прошло успешно")
                    break
                except BackoffError:
                    logging.error(f'Подключение к {servise} не установлено')
                except ConnectionError:
                    logging.error(f'Подключение к Redis не установлено')
                wait = min(start_sleep_time * 2 ** new_factor, border_sleep_time)
                new_factor += 1
                sleep(wait)

        return inner

    return func_wrapper
