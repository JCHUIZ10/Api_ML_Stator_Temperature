from datetime import datetime,timezone

from .input import Input
from .output import Output

class Data:
    __entrada : Input
    __salida : Output
    __fecha_ingreso: datetime 

    def __init__(self, entrada: Input, salida: Output):
        self.__entrada = entrada
        self.__salida = salida
        self.__fecha_ingreso = datetime.now(timezone.utc) 

    @property
    def entrada(self) -> Input:
        return self.__entrada

    @entrada.setter
    def entrada(self, nueva_entrada: Input):
        self.__entrada = nueva_entrada

    @property
    def salida(self) -> Output:
        return self.__salida

    @salida.setter
    def salida(self, nueva_salida: Output):
        self.__salida = nueva_salida

    @property
    def fecha_ingreso(self) -> datetime:
        return self.__fecha_ingreso

    def __repr__(self) ->str:
        return f"Data(entrada={self.__entrada}, salida={self.__salida}, fecha={self.__fecha_ingreso})"