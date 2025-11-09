from abc import ABC, abstractmethod

class IServicioCorreo(ABC):
    @abstractmethod
    def enviar_correo(self): pass