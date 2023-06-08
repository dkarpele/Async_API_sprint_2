from abc import ABC, abstractmethod
from typing import Optional


class AbstractStorage(ABC):
    """
    Абстрактый класс для работы с хранилищем данных.
    Описывает какие методы должны быть у подобных классов.
    get_by_id - возвращает один экземпляр класса модели,
    по которой строятся полученные из хранилища
    get_list - возвращает список объектов модели, переданной в
    качестве парараметра
    """

    @abstractmethod
    async def get_by_id(self, _id: str, index: str, model) -> Optional:
        ...

    @abstractmethod
    async def get_list(self, model, index: str, sort: str, search: dict, page: int, size: int) -> list | None:
        ...
