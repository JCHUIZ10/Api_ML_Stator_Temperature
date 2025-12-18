from typing import Optional
from domain.entity.api_status import ApiStatus
from aplication.cu.cargar_modelo_cu import ICargarModeloCasoUso
from aplication.machine_learning.modelo_predictivo_port import ModeloPredictivo
from aplication.service_port.iservicios_almacenamiento import IServicioAlmacenamiento

from infraestructure.machine_learning.random_forest_regressor import ModeloRandomForestRegressor

class CargarModeloRandomForestCasoUso(ICargarModeloCasoUso):
    """
    Caso de uso para cargar modelo RandomForest y escalador desde Google Drive.
    Utiliza gdown para descargas robustas y archivos temporales.
    """
    def __init__(self,status : ApiStatus, servicioAlmacenamiento:IServicioAlmacenamiento):
        """Inicializa las variables de instancia para mantener los objetos en memoria."""
        self.__modeloPredictivo: Optional[ModeloPredictivo] = None
        self.__status = status
        self.__servicioAlmacenamiento : IServicioAlmacenamiento = servicioAlmacenamiento
    
    def cargarModelo(self) -> None:
        """
        Descarga y carga el escalador y modelo desde Google Drive.
        Los objetos quedan disponibles en memoria para uso posterior.
        Usa archivos temporales que se eliminan automáticamente.
        
        Raises:
            Exception: Si hay error en descarga o carga de objetos
        """
        if self.__status.estado:
            print("El modelo ya está cargado en memoria.")
            return
        
        try:
            print("=" * 60)
            print("CARGANDO MODELO DESDE LA NUBE")
            print("=" * 60)
            
            # Descargar y cargar escalador
            print("\n[1] Procesando escalador...")
            self.__modelo_rf , self.__escalador = self.__servicioAlmacenamiento.descargar_modelo()
            
            #Instanciamos el modelo Random Forest
            self.__modeloPredictivo = ModeloRandomForestRegressor(self.__modelo_rf,self.__escalador)
            self.__status.set_estado(True)
            
            print("\n" + "=" * 60)
            print("✓✓✓ MODELO Y ESCALADOR LISTOS PARA USAR ✓✓✓")
            print("=" * 60)
            
        except Exception as e:
            self.__status.set_estado(False)
            self.__modeloPredictivo = None
            print(f"\nX ERROR: {str(e)}")
            raise Exception(f"Error al cargar modelo: {str(e)}")
    
    def getModelo(self) -> ModeloPredictivo:
        """
        Retorna el modelo predictivo cargado en memoria.
        
        Returns:
            RandomForestRegressor: Modelo cargado
            
        Raises:
            RuntimeError: Si el modelo no ha sido cargado
        """
        if not self.__status.estado or self.__modeloPredictivo is None:
            raise RuntimeError(
                "El modelo no está cargado. Ejecuta cargarModelo() primero."
            )
        return self.__modeloPredictivo
    
    def olvidar(self) -> None:
        """Libera los objetos de memoria si es necesario."""
        self.__modeloPredictivo = None
        self.__status.set_estado(False)
        print("Memoria liberada.")
