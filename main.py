# main.py
import sys
import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Agregar src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/'))

# Importar las clases de tu dominio y casos de uso
from src.domain.entity.input import Input
from src.domain.entity.api_status import ApiStatus
from src.infraestructure.adaptador_cu.cargar_modelo_cu_adapt import CargarModeloRandomForestCasoUso
from src.infraestructure.adaptador_cu.consultar_status_api_cu_adapt import ConsultarStatusApiCasoUso
from src.infraestructure.adaptador_cu.predecir_temperatura_cu_adapt import PredecirTemperaturaCasoUso

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

# Instancia global de los casos de uso (CU)
apiStatus = ApiStatus()
cargarModeloCU = CargarModeloRandomForestCasoUso(apiStatus)
consultarStatusCU = ConsultarStatusApiCasoUso(apiStatus)
predecirCU = PredecirTemperaturaCasoUso(cargarModeloCU, consultarStatusCU)

# Cargar el modelo cuando inicie la API (una sola vez)
cargarModeloCU.cargarModelo()

@app.get("/")
async def hola():
   return {"message": "¡Hola, tu API está funcionando!"}

@app.post("/predecir/")
async def predecir_temperatura(input_data: InputData):
    """
    Endpoint para predecir la temperatura dado un conjunto de datos de entrada.
    """
    try:
        # Convertir los datos de entrada de Pydantic a tu clase Input
        i1 = Input(**input_data.dict())

        # Realizar la predicción
        resultado = predecirCU.predecir(i1)

        return {"temperatura_predicha": resultado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))