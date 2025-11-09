from abc import ABC, abstractmethod
from domain.entity.data import Data

class IRepositoryData(ABC):
    @abstractmethod
    def guardar(self, newData:Data): pass