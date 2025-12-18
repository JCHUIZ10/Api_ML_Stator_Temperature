#Para gestionar los errores de la aplicación
from aplication.error.api_exceptions import ApiNoDisponibleError
from aplication.error.prediccion_exceptions import ErrorPrediccionError

__all__ = ["ApiNoDisponibleError","ErrorPrediccionError"]