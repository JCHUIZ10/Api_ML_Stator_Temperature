from abc import ABC, abstractmethod

class IActualizarModeloCasoUso(ABC):
    @abstractmethod
    def actualizarModeloPredictivo(self) ->None: pass