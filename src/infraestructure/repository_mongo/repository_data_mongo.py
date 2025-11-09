from domain.repository.repository_data import IRepositoryData
from domain.entity.data import Data

class RepositoryDataMemoria(IRepositoryData):
    
    __datos: list[Data] 
    
    def __init__(self):
        # Inicializa una lista vacía para almacenar los objetos Data
        self.__datos = [] 

    def guardar(self, newData: Data) ->None:
        self.__datos.append(newData)
   