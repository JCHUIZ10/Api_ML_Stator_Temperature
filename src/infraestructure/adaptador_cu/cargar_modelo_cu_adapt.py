import gdown
import joblib
import pickle
import tempfile
import os
from typing import Optional

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

from domain.entity.api_status import ApiStatus
from aplication.cu.cargar_modelo_cu import ICargarModeloCasoUso
from aplication.machine_learning.modelo_predictivo_port import ModeloPredictivo

from infraestructure.machine_learning.random_forest_regressor import ModeloRandomForestRegressor

class CargarModeloRandomForestCasoUso(ICargarModeloCasoUso):
    """
    Caso de uso para cargar modelo RandomForest y escalador desde Google Drive.
    Utiliza gdown para descargas robustas y archivos temporales.
    """

    # IDs de Google Drive
    __drive_ids = {
        "escalador": "1Xz4qMjrdkCdjpDyfqhsdIn5b-y4Aqm-R",
        "modelo": "1H6p9MTZlXpN1MWRb6gPBUZdoVE9Zd1mf"
    }
    
    def __init__(self,status : ApiStatus):
        """Inicializa las variables de instancia para mantener los objetos en memoria."""
        self.__modeloPredictivo: Optional[ModeloPredictivo] = None
        self.__status = status
    
    def __descargarYCargarArchivo(self, drive_id: str, nombre_archivo: str):
        """
        Descarga un archivo de Google Drive usando gdown y lo carga desde archivo temporal.
        El archivo temporal se elimina automáticamente después de la carga.
        
        Args:
            drive_id: ID del archivo en Google Drive
            nombre_archivo: Nombre descriptivo del archivo (para logs)
            
        Returns:
            Objeto cargado desde el archivo
            
        Raises:
            Exception: Si hay error en la descarga o carga
        """

        tmp_path = None
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp:
                tmp_path = tmp.name
            
            print(f"Descargando {nombre_archivo}...")
            
            # URL de descarga de Google Drive
            url = f"https://drive.google.com/uc?id={drive_id}"
            
            # Descargar con gdown
            gdown.download(url, tmp_path, quiet=False)
            
            # Verificar que el archivo se descargó
            if not os.path.exists(tmp_path):
                raise Exception(f"El archivo {nombre_archivo} no se descargó correctamente")
            
            # Obtener tamaño del archivo
            file_size = os.path.getsize(tmp_path)

            #Verificamos que no sea cero
            if file_size == 0:
                raise Exception(f"El archivo {nombre_archivo} está vacío")
            
            if nombre_archivo.lower() == "escalador":
                with open(tmp_path, 'rb') as f:
                    obj = pickle.load(f)
            else:  # modelo
                obj = joblib.load(tmp_path)
            
            print(f"✓ {nombre_archivo} cargado exitosamente")
            return obj
            
        except Exception as e:
            raise Exception(f"Error al procesar {nombre_archivo}: {str(e)}")
        
        finally:
            # Eliminar archivo temporal
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                    print(f"✓ Archivo temporal eliminado: {tmp_path}")
                except Exception as e:
                    print(f"⚠ No se pudo eliminar archivo temporal: {str(e)}")
    
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
            print("CARGANDO MODELO DESDE GOOGLE DRIVE")
            print("=" * 60)
            
            # Descargar y cargar escalador
            print("\n[1/2] Procesando escalador...")
            self.__escalador = self.__descargarYCargarArchivo(
                self.__drive_ids["escalador"], 
                "escalador"
            )
            
            # Descargar y cargar modelo
            print("\n[2/2] Procesando modelo...")
            self.__modelo_rf = self.__descargarYCargarArchivo(
                self.__drive_ids["modelo"], 
                "modelo"
            )
            
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
