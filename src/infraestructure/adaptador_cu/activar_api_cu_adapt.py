from aplication.cu.activar_api_cu import IActivarApiCasoUso

from domain.entity.api_status import ApiStatus

class ActivarApiCasoUso(IActivarApiCasoUso):

    __status: ApiStatus

    def __init__(self,status:ApiStatus):
        self.__status = status

    def activar(self) ->None: 
        self.__status.set_estado(True)