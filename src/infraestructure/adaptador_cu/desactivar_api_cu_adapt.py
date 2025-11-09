from aplication.cu.desactivar_api_cu import IDescativarApiCasoUso

from domain.entity.api_status import ApiStatus

class DescativarApiCasoUso(IDescativarApiCasoUso):
    __status: ApiStatus

    def __init__(self,status:ApiStatus):
        self.__status = status

    def desactivar(self) ->None: 
        self.__status.set_estado(False)