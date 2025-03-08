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

class JugadorEnRango(NodoBase):
    """Condición que verifica si el jugador está en rango de detección"""
    def __init__(self, rango_deteccion=250):
        super().__init__()
        self.rango_deteccion = rango_deteccion

    def ejecutar(self, robot, jugador_x, jugador_y):
        dx = jugador_x - robot.x
        dy = jugador_y - robot.y
        distancia = math.sqrt(dx * dx + dy * dy)
        
        return Estado.EXITO if distancia <= self.rango_deteccion else Estado.FALLO

# Nodos de comportamiento específicos
class PerseguirJugador(NodoBase):
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y):
        # Siempre mover hacia el jugador y retornar EJECUTANDO
        robot.mover_hacia_jugador(jugador_x, jugador_y)
        return Estado.EJECUTANDO


class Patrullar(NodoBase):
    def __init__(self):
        super().__init__()
        self.puntos_patrulla = None
        self.punto_actual = 0
        self.margen_llegada = 5

    def ejecutar(self, robot, jugador_x, jugador_y):
        # Si no hay puntos de patrulla, crearlos alrededor de la posición inicial del robot
        if self.puntos_patrulla is None:
            centro_x = robot.x
            centro_y = robot.y
            radio = 100  # Radio de patrulla
            self.puntos_patrulla = [
                (centro_x + radio, centro_y),
                (centro_x, centro_y + radio),
                (centro_x - radio, centro_y),
                (centro_x, centro_y - radio)
            ]

        # Obtener punto actual de patrulla
        punto_objetivo = self.puntos_patrulla[self.punto_actual]
        
        # Calcular distancia al punto objetivo
        dx = punto_objetivo[0] - robot.x
        dy = punto_objetivo[1] - robot.y
        distancia = math.sqrt(dx * dx + dy * dy)

        # Si llegamos al punto, ir al siguiente
        if distancia < self.margen_llegada:
            self.punto_actual = (self.punto_actual + 1) % len(self.puntos_patrulla)
            punto_objetivo = self.puntos_patrulla[self.punto_actual]

        # Mover hacia el punto objetivo
        robot.mover_hacia_objetivo(punto_objetivo[0], punto_objetivo[1])
        return Estado.EJECUTANDO