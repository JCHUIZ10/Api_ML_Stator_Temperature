from abc import ABC, abstractmethod
from domain.entity import Input, Output

class IPredecirTemperaturaCasoUso(ABC):
    @abstractmethod
    def predecir(self,dataEntrada:Input) -> Output|None: pass