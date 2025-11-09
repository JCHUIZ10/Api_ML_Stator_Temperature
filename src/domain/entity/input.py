class Input:
    __ambiente :float       #Temperatura del ambiente en C°
    __coolant :float        #Temperatura de refrigeracion del motor C°
    __u_d :float            #Tensión del componente d 
    __u_q :float            #Tensión del componente Q 
    __motor_speed :float    #Velocidad del motor
    __i_d :float            #Corriente del componente D 
    __i_q :float            #Corriente del componente q

    def __init__(self, ambiente: float, coolant: float,
                 u_d: float, u_q: float, motor_speed: float,
                 i_d: float, i_q: float):
        # Usamos __ (Doble _) para encapsular el atributo
        self.__ambiente = ambiente
        self.__coolant = coolant
        self.__u_d = u_d
        self.__u_q = u_q
        self.__motor_speed = motor_speed
        self.__i_d = i_d
        self.__i_q = i_q

    # Propiedad para 'ambiente'
    @property
    def ambiente(self) -> float:
        return self.__ambiente

    @ambiente.setter
    def ambiente(self, valor: float):
        self.__ambiente = valor

    # Propiedad para 'coolant'
    @property
    def coolant(self) -> float:
        return self.__coolant

    @coolant.setter
    def coolant(self, valor: float):
        self.__coolant = valor

    # Propiedad para 'u_d'
    @property
    def u_d(self) -> float:
        return self.__u_d

    @u_d.setter
    def u_d(self, valor: float):
        self.__u_d = valor

    # Propiedad para 'u_q'
    @property
    def u_q(self) -> float:
        return self.__u_q

    @u_q.setter
    def u_q(self, valor: float):
        self.__u_q = valor

    # Propiedad para 'motor_speed'
    @property
    def motor_speed(self) -> float:
        return self.__motor_speed

    @motor_speed.setter
    def motor_speed(self, valor: float):
        self.__motor_speed = valor

    # Propiedad para 'i_d'
    @property
    def i_d(self) -> float:
        return self.__i_d

    @i_d.setter
    def i_d(self, valor: float):
        self.__i_d = valor

    # Propiedad para 'i_q'
    @property
    def i_q(self) -> float:
        return self.__i_q

    @i_q.setter
    def i_q(self, valor: float):
        self.__i_q = valor

    def __repr__(self) ->str:
        return f"Data(entrada={self.__ambiente} ,{self.__coolant} ,{self.__u_d} ,{self.__u_q} ,{self.__motor_speed} ,{self.__i_d} ,{self.__i_q} )"