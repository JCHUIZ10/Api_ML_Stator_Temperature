from abc import ABC, abstractmethod

class IActivarApiCasoUso(ABC):
    @abstractmethod
    def activar(self) ->None: pass