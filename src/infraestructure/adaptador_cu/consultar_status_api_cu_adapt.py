from aplication.cu.consultar_status_api_cu import IConsultarStatusApiCasoUso

from domain.entity.api_status import ApiStatus

class ConsultarStatusApiCasoUso(IConsultarStatusApiCasoUso):
    __status: ApiStatus

    def __init__(self,status:ApiStatus):
        self.__status = status

    def getEstadoApi(self) -> bool:
        return self.__status.estado