from dropbox import Dropbox, exceptions
from dropbox.files import (
    FileMetadata,
    FolderMetadata,
    UploadSessionCursor,
    CommitInfo,
    WriteMode
)
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from io import BytesIO 
from aplication.service_port.iservicios_almacenamiento import IServicioAlmacenamiento

import joblib
import os

class GestorDropbox(IServicioAlmacenamiento):
    """Clase para gestionar la descarga, subida y archivado de modelos de ML en Dropbox."""

    # --- Configuración Estática ---
    RUTA_PRODUCCION: str = "/produccion"
    NOMBRE_MODELO: str = "modelo_regresion.joblib"
    NOMBRE_SCALER: str = "scaler_datos.pkl"
    cliente: Dropbox

    def __init__(self):
        # 1. Asegurar la obtención del token
        self.DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
        
        if not self.DROPBOX_TOKEN:
             raise ValueError("DROPBOX_TOKEN no está configurado como variable de entorno.")

        # 2. Inicializar el cliente
        self.cliente = Dropbox(self.DROPBOX_TOKEN)

        # 3. Definir CHUNK_SIZE
        self.tamaño_session = 4 * 1024 * 1024

    def descargar_modelo(self) -> tuple:
        """
        Descarga el modelo y scaler activos de producción y los carga
        directamente a la memoria como objetos Python.

        Retorna: (modelo_obj, scaler_obj)
        """

        # Rutas completas a los archivos
        ruta_modelo = self.RUTA_PRODUCCION + "/" + self.NOMBRE_MODELO
        ruta_scaler = self.RUTA_PRODUCCION + "/" + self.NOMBRE_SCALER

        print(f"Buscando modelo en: {ruta_modelo}")

        try:
            # --- DESCARGA Y CARGA DEL MODELO (Joblib) ---
            # El método files_download retorna (metadata, response)
            _, response_mod = self.cliente.files_download(ruta_modelo) # type: ignore

            # El contenido binario se carga directamente a joblib a través de BytesIO
            modelo_obj: RandomForestRegressor = joblib.load(BytesIO(response_mod.content))
            print("Modelo descargado exitosamente.")

            # --- DESCARGA Y CARGA DEL SCALER (Joblib o Pickle) ---
            _, response_sca = self.cliente.files_download(ruta_scaler) # type: ignore

            # Usar joblib.load para consistencia con el modelo (asumiendo que es joblib)
            # Si usas .pkl, joblib.load() funciona para ambos.
            scaler_obj: StandardScaler = joblib.load(BytesIO(response_sca.content))
            print("Scaler descargado exitosamente.")

            print("Modelo y Scaler de producción cargados exitosamente a la memoria.")
            return modelo_obj, scaler_obj

        except exceptions.ApiError as e:
            if 'path/not_found' in str(e):
                print(f"Error: Uno o ambos archivos no fueron encontrados en Dropbox.")
                return None, None
            raise

    def listar_carpeta(self, ruta: str) -> None:
        """
        Lista el contenido (archivos y carpetas) de una ruta específica en Dropbox.
        Maneja la paginación de resultados.
        """
        print(f"Contenido de '{ruta}':")

        try:
            # 1. Llamada inicial a la API
            result = self.cliente.files_list_folder(ruta)

            # Bucle para manejar la paginación (si hay más de 2000 resultados)
            while True:
                for entry in result.entries: # type: ignore
                    # 2. Distinguir si es carpeta o archivo
                    if isinstance(entry, FolderMetadata):
                        tipo = "-- Carpeta"
                    elif isinstance(entry, FileMetadata):
                        tipo = "* Archivo"
                    else:
                        tipo = "* Desconocido"

                    print(f" - {tipo}: {entry.name}")

                # 3. Verificar si hay más páginas de resultados
                if result.has_more: # type: ignore
                    print("... Obteniendo más resultados (paginación)...")
                    result = self.cliente.files_list_folder_continue(result.cursor) # type: ignore
                else:
                    break # Salir del bucle si no hay más resultados

            print("--- Listado completo ---")

        except exceptions.ApiError as e:
            # Capturar el error si la carpeta no existe
            if 'path/not_found' in str(e):
                print(f"Error: La ruta '{ruta}' no fue encontrada en Dropbox.")
            else:
                print(f"Error de API de Dropbox: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")

    # El método principal de subida es correcto y no necesita cambios
    def subir_a_dropbox_a_produccion(self, modelo, scaler) -> bool:
        # ... (Tu código para llamar a _subir_objeto)
        try:
            # 1. Subir el Modelo
            self._subir_objeto(
                modelo,
                self.NOMBRE_MODELO,
                self.RUTA_PRODUCCION
            )

            # 2. Subir el Scaler
            self._subir_objeto(
                scaler,
                self.NOMBRE_SCALER,
                self.RUTA_PRODUCCION
            )

            print("\n Despliegue de Producción COMPLETO.")
            return True

        except Exception:
            print("El despliegue falló. Revisar el error anterior.")
            return False


    def _subir_objeto(self, objeto, nombre_archivo: str, ruta_base: str):
        """
        Método auxiliar robusto que usa Subida por Sesiones (Upload Sessions)
        para manejar archivos grandes (> 150 MB).
        """

        ruta_completa_dropbox = f"{ruta_base}/{nombre_archivo}"

        # 1. Serializar el objeto en un buffer de memoria y obtener el tamaño
        buffer = BytesIO()
        joblib.dump(objeto, buffer)
        buffer.seek(0)
        file_size = buffer.getbuffer().nbytes

        print(f"Subiendo {nombre_archivo} a {ruta_completa_dropbox} ({file_size / (1024*1024):.2f} MB)...")

        # 2. Iniciar la subida por Sesiones
        try:
            # Leer el primer fragmento (Chunk)
            data = buffer.read(self.tamaño_session)

            # Iniciar la sesión de subida
            session_start_result = self.cliente.files_upload_session_start(data)
            cursor = UploadSessionCursor(
                session_id=session_start_result.session_id, # type: ignore
                offset=buffer.tell()
            )

            # 3. Subir los fragmentos intermedios
            while buffer.tell() < file_size:
                data = buffer.read(self.tamaño_session)

                if buffer.tell() < file_size:
                    # Appendir fragmentos (si no es el último)
                    self.cliente.files_upload_session_append_v2(data, cursor)
                    cursor.offset = buffer.tell()
                else:
                    # 4. Finalizar la sesión (último fragmento)
                    self.cliente.files_upload_session_finish(
                        data,
                        cursor,
                        commit=CommitInfo(
                            path=ruta_completa_dropbox,
                            mode=WriteMode.overwrite
                        )
                    )

            print(f"{nombre_archivo} subido correctamente.")

        except Exception as e:
            print(f"Error al subir {nombre_archivo} usando Sesiones: {e}")
            raise # Re-lanzar la excepción