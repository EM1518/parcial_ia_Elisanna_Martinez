import math

class Estado:
    EXITO = "EXITO"
    FALLO = "FALLO"
    EJECUTANDO = "EJECUTANDO"

class NodoBase:
    def __init__(self):
        self.estado = Estado.EJECUTANDO

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        pass

class Secuencia(NodoBase):
    """Ejecuta nodos hijos en orden hasta que uno falle"""
    def __init__(self, nodos):
        super().__init__()
        self.nodos = nodos
        self.nodo_actual = 0

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        while self.nodo_actual < len(self.nodos):
            estado = self.nodos[self.nodo_actual].ejecutar(robot, jugador_x, jugador_y, otros_robots)
            
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

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        while self.nodo_actual < len(self.nodos):
            estado = self.nodos[self.nodo_actual].ejecutar(robot, jugador_x, jugador_y, otros_robots)
            
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
    def __init__(self, rango_deteccion=150):
        super().__init__()
        self.rango_deteccion = rango_deteccion

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        dx = jugador_x - robot.x
        dy = jugador_y - robot.y
        distancia = math.sqrt(dx * dx + dy * dy)
        
        return Estado.EXITO if distancia <= self.rango_deteccion else Estado.FALLO

# Nodos de comportamiento específicos
class Perseguir(NodoBase):
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        # Siempre mover hacia el jugador y retornar EJECUTANDO
        robot.mover_hacia_jugador(jugador_x, jugador_y, otros_robots)
        return Estado.EJECUTANDO


class Patrullar(NodoBase):
    """Comportamiento de patrulla"""
    def __init__(self):
        super().__init__()
        self.puntos_patrulla =  []
        self.punto_actual = 0
        self.margen_llegada = 5

    def inicializar_puntos(self, robot):
        """Inicializa los puntos de patrulla si no existen"""
        if not self.puntos_patrulla:
            # Crear un patrón rectangular alrededor del punto inicial
            x_base = robot.x
            y_base = robot.y
            offset = 75  # Distancia del patrón de patrulla
            
            self.puntos_patrulla = [
                (x_base + offset, y_base),
                (x_base + offset, y_base + offset),
                (x_base, y_base + offset),
                (x_base, y_base)
            ]

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        self.inicializar_puntos(robot)
        
        # Obtener punto actual de de destino
        punto_actual = self.puntos_patrulla[self.punto_actual]

        
        # Verificar si llegamos al punto
        dx = punto_objetivo[0] - robot.x
        dy = punto_objetivo[1] - robot.y
        distancia = math.sqrt(dx * dx + dy * dy)
        
        if distancia < self.margen_llegada:
            # Avanzar al siguiente punto
            self.punto_actual = (self.punto_actual + 1) % len(self.puntos_patrulla)
        
        # Mover hacia el punto
        robot.mover_hacia_objetivo(punto_actual[0], punto_objetivo[1], otros_robots)            
        return Estado.EJECUTANDO