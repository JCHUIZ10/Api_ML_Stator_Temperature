from aplication.cu.predecir_temperatura_cu import IPredecirTemperaturaCasoUso

from domain.entity import Input, Output

from aplication.cu.cargar_modelo_cu import ICargarModeloCasoUso
from aplication.cu.consultar_status_api_cu import IConsultarStatusApiCasoUso
from aplication.error import ApiNoDisponibleError, ErrorPrediccionError

class PredecirTemperaturaCasoUso(IPredecirTemperaturaCasoUso):
    __cargarModeloCU : ICargarModeloCasoUso
    __consultarStatusCU : IConsultarStatusApiCasoUso

    #Aquie debe exitir un objeto que controle ciclo de vida del modelo
    def __init__(self,cargarModeloCU: ICargarModeloCasoUso,consultarStatusCU : IConsultarStatusApiCasoUso) -> None:
        self.__cargarModeloCU = cargarModeloCU
        self.__consultarStatusCU = consultarStatusCU

    def predecir(self, dataEntrada: Input) -> Output | None:
        try:
            print("Estado API:", self.__consultarStatusCU.getEstadoApi())

            if not self.__consultarStatusCU.getEstadoApi():
                raise ApiNoDisponibleError("API no disponible para predicciones.")

            modelo = self.__cargarModeloCU.getModelo()
            out = modelo.ejecutar(dataEntrada)
            return out

        except ApiNoDisponibleError:
            raise
        except Exception as e:
            raise ErrorPrediccionError(f"Error en PredecirTemperaturaCasoUso: {str(e)}") from e