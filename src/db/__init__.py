from abc import ABC, abstractmethod
from typing import Optional


class AbstractStorage(ABC):
    """
    Абстрактый класс для работы с хранилищем данных.
    Описывает какие методы должны быть у подобных классов.
    get_by_id - возвращает один экземпляр класса модели,
    по которой строятся полученные из хранилища
    get_list - возвращает список объектов модели, переданной в
    качестве параметра.
    """

    @abstractmethod
    async def get_by_id(self, _id: str, index: str, model) -> Optional:
        """
        Абстрактный асинхронный метод для получения данных по id
        :param _id: строка с id, по которому выполняется поиск
        :param index: строковое название индекса, в котором выполняется поиск
        :param model: тип модели, в котором возвращаются данные
        :return: объект типа, заявленного в model
        """
        ...

    @abstractmethod
    async def get_list(self, model, index: str, sort: str, search: dict,
                       page: int, size: int) -> list | None:
        """
        Абстрактный асинхронный метод для получения списка данных
        :param model: тип модели, в котором возвращаются данные
        :param index: строковое название индекса, в котором выполняется поиск
        :param sort: строка с названием атрибута, по которой необходима
        сортировка
        :param search: словарь с параметрами для поиска, если они необходимы
        :param page: номер страницы
        :param size: количество элементов на странице(в списке)
        :return: список объектов типа model
        """
        ...
