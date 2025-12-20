from aplication.service_port.pipeline_autoentrenamiento import PipelineAutoentrenamiento
from aplication.cu.cargar_modelo_cu import ICargarModeloCasoUso

class ActualizarModeloCasoUso:

    def __init__(self,autoentrenamiento: PipelineAutoentrenamiento,cargarModelo : ICargarModeloCasoUso ):
        self.__servicioAutoentrenamiento = autoentrenamiento
        self.__cargarModelo = cargarModelo

    def actualizarModeloPredictivo(self) -> None:
        mejor = self.__servicioAutoentrenamiento.star()
        if mejor :
            self.__cargarModelo.olvidar()
            self.__cargarModelo.cargarModelo()