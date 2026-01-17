from typing import Tuple
import pandas as pd
import numpy as np
import logging

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from src.infraestructure.repository.train_dataset import RepositoryPosgrestTrain
from src.infraestructure.service_adapt.service_dropbox import GestorDropbox
from src.infraestructure.service_adapt.service_correo_gmail import ServiceCorreoGmail
from src.aplication.service_port.pipeline_autoentrenamiento import PipelineAutoentrenamiento

logger = logging.getLogger(__name__)

class ServicioAutoentrenamiento(PipelineAutoentrenamiento):

    columnas_deseadas = [
        'ambiente',             # Temperaturaambiente (IN)
        'refrigeracion',        # Temperatura del refrigerante (IN)
        'voltaje_d',            # Tensión del componente d (IN)
        'voltaje_q',            # Tensión del componente q (IN)
        'velocidad',            # Velocidad del motor (IN)
        'corriente_d',          # Corriente del componente D (IN)
        'corriente_q',          # Corriente del componente q (IN)
        'temperatura'           # Temperatura del bobinado del estator (OUT)
    ]

    escalador:StandardScaler
    modelo:RandomForestRegressor
    gestorAlmacenamiento : GestorDropbox
    servicioCorreo : ServiceCorreoGmail


    def __init__(self):
        self.repositoryTrain = RepositoryPosgrestTrain()
        self.gestorAlmacenamiento = GestorDropbox()
        self.servicioCorreo = ServiceCorreoGmail()
        
    
    def star(self) -> bool:
        try:
            logger.info("Se inicializo el proceso de autoentrenamiento")
            df = self.repositoryTrain.obtener_data_train()
            logger.info("Se obtuvo la dataset exitosamente")

            X_train_scaled, X_test, y_train, y_test = self.__preprocesar(df) # type: ignore
            logger.info("Culiminación exitosa del preprocesamiento")

            self.modelo = self.__entrenar(X_train_scaled,y_train)
            logger.info("Culiminación exitosa del proceso de entrenamiento")

            modelo_old, scalar_old = self.gestorAlmacenamiento.descargar_modelo()
            logger.info("Obtención exitosa del modelo y escalador actuales en produccion")

            X_train_scaled, X_test, y_train, y_test = self.__preprocesar(df) # type: ignore
            respuesta:bool = self.evaluar_modelo_nuevo(modelo_old, self.modelo, scalar_old, self.escalador, X_test, y_test)

            if respuesta:
                logger.info("El 'nuevo modelo' es mejor, sera actualizado a producción")
                self.gestorAlmacenamiento.subir_a_dropbox_a_produccion(self.modelo, self.escalador)
                self.servicioCorreo.enviar_correo("Se actualizo exitosamente el modelo de prediccion") 
            else:
                logger.info("El 'nuevo modelo' es no es mejor, se mantendra el modelo actual en producción")
                self.servicioCorreo.enviar_correo("Se finalizo exitosamente el proceso de auto-entrenamiento, pero no se actualizo") 
            
            return respuesta
        except Exception as e:
            logger.error("ERROR : {e}")
            self.servicioCorreo.enviar_correo("Sucedio un error en el proceso de auto-entrenamiento") 
            return False

    def __preprocesar(self, df_vista:pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame, pd.Series, pd.Series]:
        #Eliminamos las columnas que no nos funcionaran
        dfClean = df_vista[self.columnas_deseadas]

        #Segregar los Variables Dependientes (X) - Variables Independientes(Y)
        X = dfClean.drop("temperatura", axis=1)
        y = dfClean["temperatura"]

        #Particionar Dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info(X_train.shape, y_train.shape)
        logger.info(X_test.shape, y_test.shape)

        #Instanciamos el scalador (normalizar Datos)
        self.escalador = StandardScaler()
        #Creamos un escalador Ajustado a la dataset
        X_train_scaled = self.escalador.fit_transform(X_train)

        return  X_train_scaled, X_test, y_train, y_test
    
    def __entrenar(self,X_train_scaled, y_train):
        model:RandomForestRegressor = RandomForestRegressor(
            n_estimators=200,   #cuántos árboles tendrá el bosque.
            max_depth=15,       #Qué tan profundo puede crecer cada árbol.
            min_samples_split=5,#mínimo de muestras para dividir un nodo.
            random_state=42,    #hace que el modelo dé el mismo resultado cada vez.
            n_jobs=-1,           #cuántos núcleos de CPU se usan en paralelo.
            verbose=1  # <- muestra progreso en consola
        )

        return model.fit(X_train_scaled, y_train)
    
    def evaluar_modelo_nuevo(self, modelo_old, modelo_new, scalar_old, scalar_new, X_test, y_true) -> bool:
        """
        Compara el rendimiento de dos modelos de regresión y determina si el
        modelo nuevo es significativamente mejor que el antiguo.

        Args:
            modelo_old: El modelo de regresión de referencia (antiguo).
            modelo_new: El modelo de regresión a evaluar (nuevo).
            X_test: Características del conjunto de prueba.
            y_true: Valores reales (verdaderos) del conjunto de prueba.

        Returns:
            True si el modelo nuevo es mejor, False en caso contrario.
        """

        #1. El modelo antiguo debe recibir datos escalados por el escalador antiguo
        X_test_scaled_old = scalar_old.transform(X_test)
        y_pred_old = modelo_old.predict(X_test_scaled_old) # Uso de datos escalados

        #2. El modelo nuevo debe recibir datos escalados por el escalador nuevo
        X_test_scaled_new = scalar_new.transform(X_test)
        y_pred_new = modelo_new.predict(X_test_scaled_new) # Uso de datos escalados

        # 3. Calcular Métricas para el modelo antiguo
        r2_old = r2_score(y_true, y_pred_old)
        rmse_old = np.sqrt(mean_squared_error(y_true, y_pred_old))

        # 4. Calcular Métricas para el modelo nuevo
        r2_new = r2_score(y_true, y_pred_new)
        rmse_new = np.sqrt(mean_squared_error(y_true, y_pred_new))

        logger.warning("--- Resultados de la Evaluación ---")
        logger.warning(f"Modelo Antiguo (Old) - R²: {r2_old:.4f}, RMSE: {rmse_old:.4f}")
        logger.warning(f"Modelo Nuevo (New) - R²: {r2_new:.4f}, RMSE: {rmse_new:.4f}")
        logger.warning("-----------------------------------")

        # 4. Criterios de Decisión Sólidos

        # CRITERIO 1: El R² (explicación de la varianza) DEBE ser mejor (más alto)
        mejora_r2 = r2_new > r2_old

        # CRITERIO 2: El RMSE (magnitud del error) DEBE ser mejor (más bajo)
        mejora_rmse = rmse_new < rmse_old

        # El modelo nuevo es mejor si MEJORA en AMBOS criterios
        if mejora_r2 and mejora_rmse:
            logger.info("El Modelo Nuevo es MEJOR: Mejor R² Y menor RMSE.")
            return True

        # Si mejora en uno y no empeora en el otro (con un umbral de tolerancia, ej: 0.1% de tolerancia)
        # Esto es útil para evitar declarar empate por un cambio infinitesimal
        tolerancia_porcentual = 0.001  # 0.1% de tolerancia

        # R²: Permitir que el R² no baje más de un 0.1%
        casi_igual_r2 = r2_new >= r2_old * (1 - tolerancia_porcentual)
        # RMSE: Permitir que el RMSE no suba más de un 0.1%
        casi_igual_rmse = rmse_new <= rmse_old * (1 + tolerancia_porcentual)

        if (mejora_r2 and casi_igual_rmse) or (mejora_rmse and casi_igual_r2):
            logger.info("El Modelo Nuevo es SIMILAR: Mejora en una métrica y es casi igual en la otra.")
            # En este caso, si la meta es solo 'True si es mejor', retornamos False
            return False

        logger.info("El Modelo Nuevo NO es mejor: No mejoró en ambas métricas clave.")
        return False
