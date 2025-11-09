from abc import ABC, abstractmethod

from aplication.machine_learning.modelo_predictivo_port import ModeloPredictivo

class ICargarModeloCasoUso(ABC):
    @abstractmethod
    def cargarModelo(self) -> None : pass

    @abstractmethod
    def getModelo(self) -> ModeloPredictivo: pass 

    @abstractmethod
    def olvidar(self) -> None : pass