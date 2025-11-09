from abc import ABC, abstractmethod

class IDescativarApiCasoUso(ABC):
    @abstractmethod
    def desactivar(self) ->None: pass