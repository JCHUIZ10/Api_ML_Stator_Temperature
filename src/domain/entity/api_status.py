class ApiStatus:
    __activo:bool

    #Constructor
    def __init__(self):
        self.__activo = False

    # Propiedad para 'estado'
    @property
    def estado(self) -> bool:
        return self.__activo
    
    #Setter para cambiar el valor del estado
    def set_estado(self, nuevoEstado: bool):
        self.__activo = nuevoEstado

    #Para imprimir 
    def __repr__(self):
        return f"ApiStatus(estado ='{self.__activo}')"