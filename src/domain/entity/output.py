class Output:
    __stator_winding:float #Temperatura del bobinado del estator

    #Constructor
    def __init__(self,stator_winding:float):
        self.__stator_winding = stator_winding

    # Propiedad para 'stator_winding'
    @property
    def estado(self) -> float:
        return self.__stator_winding

    #Para imprimir 
    def __repr__(self):
        return f"Output(stator_winding ='{self.__stator_winding}')"