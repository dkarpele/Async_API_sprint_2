from abc import ABC, abstractmethod


class AbstractStorage(ABC):

    @abstractmethod
    async def get_by_id(self, _id, index, model):
        ...

    @abstractmethod
    async def get_list(self, model, index, sort, search, page, size):
        ...
