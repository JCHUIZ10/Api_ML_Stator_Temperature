from abc import ABC, abstractmethod

class IConsultarStatusApiCasoUso(ABC):
    @abstractmethod
    def getEstadoApi(self) ->bool: pass