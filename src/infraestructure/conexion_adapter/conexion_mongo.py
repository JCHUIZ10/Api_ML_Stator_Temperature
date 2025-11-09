from pymongo import MongoClient
from pymongo.database import Database
from aplication.conexion_port import IConexion


class ConexionMongo(IConexion[Database]):
    __client: MongoClient

    def __init__(self, bd: str):
        """
        Inicializar el gestor de MongoDB
        
        Args:
            database_name: Nombre de la base de datos
        """
        self.__database_name = bd
        self.__client = self.__connect()
        self.db = self.__client[self.__database_name]
        print("Conexion Exitosa")

    def __connect(self) -> MongoClient:
        """Establecer conexión con MongoDB"""
        return MongoClient(
            serverSelectionTimeoutMS=5000,  # Tiempo máx. esperando respuesta del servidor
            connectTimeoutMS=10000,        # Tiempo máx. intentando establecer conexión
            maxPoolSize=50                 # Tamaño máximo del pool de conexiones
        )

    def getConexion(self) -> Database:
        """Obtener la base de datos activa"""
        return self.db

    def disconnect(self):
        """Cerrar conexión con MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
