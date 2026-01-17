# main.py
import sys
import os
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Agregar src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/'))

# Importar las clases de tu dominio y casos de uso
from src.domain.entity.input import Input
from src.domain.entity.api_status import ApiStatus
from src.aplication.error import ApiNoDisponibleError, ErrorPrediccionError
from src.infraestructure.adaptador_cu.cargar_modelo_cu_adapt import CargarModeloRandomForestCasoUso
from src.infraestructure.adaptador_cu.consultar_status_api_cu_adapt import ConsultarStatusApiCasoUso
from src.infraestructure.adaptador_cu.predecir_temperatura_cu_adapt import PredecirTemperaturaCasoUso
from src.infraestructure.adaptador_cu.actualizar_modelo_cu import ActualizarModeloCasoUso

from src.infraestructure.service_adapt.service_dropbox import GestorDropbox
from src.infraestructure.service_adapt.servicio_autoentrenamiento import ServicioAutoentrenamiento

from src.infraestructure.configuration.logging_config import setup_logging

#Iniciamos el loggin
setup_logging()

# Iniciar la aplicación FastAPI
app = FastAPI()

# Pydantic models para validar la entrada (Input)
class InputData(BaseModel):
    ambiente: float
    coolant: float
    u_d: float
    u_q: float
    motor_speed: float
    i_d: float
    i_q: float

#Cargar Variables de Entorno
load_dotenv() 

# Instancia global de los casos de uso (CU)
apiStatus = ApiStatus()
gestorDropbox = GestorDropbox()
servicioAutoentrenamiento = ServicioAutoentrenamiento()

cargarModeloCU = CargarModeloRandomForestCasoUso(apiStatus, gestorDropbox)
consultarStatusCU = ConsultarStatusApiCasoUso(apiStatus)
predecirCU = PredecirTemperaturaCasoUso(cargarModeloCU, consultarStatusCU)
actualizarModeloCU = ActualizarModeloCasoUso(servicioAutoentrenamiento, cargarModeloCU )

# Cargar el modelo cuando inicie la API (una sola vez)
cargarModeloCU.cargarModelo()

@app.post("/predecir/",tags=["Predicción de Temperatura del Estátor"])
async def predecir_temperatura(input_data: InputData):
    """
    Endpoint para predecir la temperatura dado un conjunto de datos de entrada.
    """
    try:
        i1 = Input(**input_data.model_dump())
        resultado = predecirCU.predecir(i1)

        return {"temperatura_predicha": resultado}

    except(ApiNoDisponibleError, ErrorPrediccionError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/auto-entrenamiento/",tags=["Iniciar Pipeline de Auto-entrenamiento"])
async def autoentrenar(background_tasks: BackgroundTasks):
    """
    Endpoint para iniciar el autoentrenamiento.
    """
    try:
        # Ejecutar en background (como tarea asíncrona) -> Evita bloquear la API ;_;
        background_tasks.add_task(actualizarModeloCU.actualizarModeloPredictivo)
        return {"mensaje": "Proceso de autoentrenamiento iniciado en segundo plano."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)