import numpy
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

from aplication.machine_learning.modelo_predictivo_port import ModeloPredictivo
from domain.entity import Input, Output

class ModeloRandomForestRegressor(ModeloPredictivo):
    __escalador: StandardScaler
    __modelo_rf: RandomForestRegressor

    def __init__(self,modelo:RandomForestRegressor, escalador:StandardScaler ) -> None:
        self.__escalador = escalador 
        self.__modelo_rf =  modelo

    def ejecutar(self,dataEntrada:Input) -> Output:
        #Obtener los valores del Input como una lista o arreglo numpy
        x = numpy.array([[
                    dataEntrada.ambiente,
                    dataEntrada.coolant,
                    dataEntrada.u_d,
                    dataEntrada.u_q,
                    dataEntrada.motor_speed,
                    dataEntrada.i_d,
                    dataEntrada.i_q
                ]])
        
        #Escalamos los datos
        x_escalado = self.__escalador.transform(x)

        #Obtenemosla predicción del modelo RandomForestRegressor
        y_pred = self.__modelo_rf.predict(x_escalado)
        
        #Casteamos el valor deseado a predecir
        temperatura_motor = float(y_pred[0])
        
        return Output(temperatura_motor)