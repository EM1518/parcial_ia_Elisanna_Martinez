class Estado:
    EXITO = "EXITO"
    FALLO = "FALLO"
    EJECUTANDO = "EJECUTANDO"

class NodoBase:
    def __init__(self):
        self.estado = Estado.EJECUTANDO

    def ejecutar(self, robot, jugador_x, jugador_y):
        pass

class Secuencia(NodoBase):
    """Ejecuta nodos hijos en orden hasta que uno falle"""
    def __init__(self, nodos):
        super().__init__()
        self.nodos = nodos
        self.nodo_actual = 0

    def ejecutar(self, robot, jugador_x, jugador_y):
        while self.nodo_actual < len(self.nodos):
            estado = self.nodos[self.nodo_actual].ejecutar(robot, jugador_x, jugador_y)
            
            if estado == Estado.FALLO:
                self.nodo_actual = 0
                return Estado.FALLO
            
            if estado == Estado.EJECUTANDO:
                return Estado.EJECUTANDO
            
            self.nodo_actual += 1

        self.nodo_actual = 0
        return Estado.EXITO

class Selector(NodoBase):
    """Ejecuta nodos hijos en orden hasta que uno tenga éxito"""
    def __init__(self, nodos):
        super().__init__()
        self.nodos = nodos
        self.nodo_actual = 0

    def ejecutar(self, robot, jugador_x, jugador_y):
        while self.nodo_actual < len(self.nodos):
            estado = self.nodos[self.nodo_actual].ejecutar(robot, jugador_x, jugador_y)
            
            if estado == Estado.EXITO:
                self.nodo_actual = 0
                return Estado.EXITO
            
            if estado == Estado.EJECUTANDO:
                return Estado.EJECUTANDO
            
            self.nodo_actual += 1

        self.nodo_actual = 0
        return Estado.FALLO

# Nodos de comportamiento específicos
class PerseguirJugador(NodoBase):
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y):
        # Siempre mover hacia el jugador y retornar EJECUTANDO
        robot.mover_hacia_jugador(jugador_x, jugador_y)
        return Estado.EJECUTANDO