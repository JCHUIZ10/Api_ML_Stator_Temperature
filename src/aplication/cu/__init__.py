#Casos de Uso del Estado de la API
from aplication.cu.activar_api_cu import IActivarApiCasoUso
from aplication.cu.desactivar_api_cu import IDescativarApiCasoUso
from aplication.cu.consultar_status_api_cu import IConsultarStatusApiCasoUso

#Casos de Uso de cliclo de Vida del Modelo
from aplication.cu.actualizar_modelo_cu import IActualizarModeloCasoUso
from aplication.cu.predecir_temperatura_cu import IPredecirTemperaturaCasoUso
from aplication.cu.cargar_modelo_cu import ICargarModeloCasoUso


__all__ = ["IPredecirTemperaturaCasoUso","IActualizarModeloCasoUso",
           "IConsultarStatusApiCasoUso","IActivarApiCasoUso","IDescativarApiCasoUso",
           "ICargarModeloCasoUso"]