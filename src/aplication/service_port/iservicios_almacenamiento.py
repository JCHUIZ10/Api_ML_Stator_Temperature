from abc import ABC, abstractmethod

class IServicioAlmacenamiento(ABC):

    @abstractmethod
    def descargar_modelo(self) -> tuple :pass

    @abstractmethod
    def listar_carpeta(self, ruta: str) -> None:pass

    @abstractmethod
    def subir_a_dropbox_a_produccion(self, modelo, scaler) -> bool: pass