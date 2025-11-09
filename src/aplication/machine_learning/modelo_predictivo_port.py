from abc import ABC, abstractmethod

from domain.entity import Input, Output

class ModeloPredictivo(ABC):
    @abstractmethod
    def ejecutar(self,dataEntrada:Input) -> Output: pass