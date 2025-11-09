from abc import ABC, abstractmethod
from typing import TypeVar, Generic

C = TypeVar("C")

class IConexion(ABC,Generic[C]):
    @abstractmethod
    def getConexion(self) -> C: pass
    