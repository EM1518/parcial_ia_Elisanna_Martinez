
def calcular_distancia(x1, y1, x2, y2):
    """Calcula la distancia euclidiana entre dos puntos"""
    dx = x2 - x1
    dy = y2 - y1

    return (dx * dx + dy * dy) ** 0.5

def normalizar_vector(dx, dy):
    magnitud = calcular_distancia(0, 0, dx, dy)

    if magnitud != 0:
        return dx / magnitud, dy / magnitud

    return 0, 0


class Estado:
    EXITO = "EXITO"
    FALLO = "FALLO"
    EJECUTANDO = "EJECUTANDO"

class NodoBase:
    def __init__(self):
        self.estado = Estado.EJECUTANDO

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        pass

class Secuencia(NodoBase):
    """Ejecuta nodos hijos en orden hasta que uno falle"""
    def __init__(self, nodos):
        super().__init__()
        self.nodos = nodos
        self.nodo_actual = 0

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        while self.nodo_actual < len(self.nodos):
            estado = self.nodos[self.nodo_actual].ejecutar(robot, jugador_x, jugador_y, otros_robots, laberinto, forzar_patrulla)
            
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

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Resetea el índice al inicio para evaluar todos los nodos cada vez
        self.nodo_actual = 0

        while self.nodo_actual < len(self.nodos):
            estado = self.nodos[self.nodo_actual].ejecutar(robot, jugador_x, jugador_y, otros_robots, laberinto, forzar_patrulla)
            
            if estado == Estado.EXITO:
                return Estado.EXITO

            # Si el nodo está en ejecución, mantenemos ese nodo activo
            if estado == Estado.EJECUTANDO:
                return Estado.EJECUTANDO

            # Si falló, pasamos al siguiente nodo
            self.nodo_actual += 1

        # Si todos los nodos fallaron, el selector falla
        return Estado.FALLO

class JugadorEnRango(NodoBase):
    """Verifica si el jugador está en rango de detección"""
    def __init__(self, rango_deteccion=500):
        super().__init__()
        self.rango_deteccion = rango_deteccion

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Si se fuerza patrulla, siempre falla
        if forzar_patrulla:
            return Estado.FALLO

        # Calculamos posiciones centrales
        robot_centro_x = robot.x + robot.ancho / 2
        robot_centro_y = robot.y + robot.alto / 2
        jugador_centro_x = jugador_x + robot.ancho / 2
        jugador_centro_y = jugador_y + robot.alto / 2

        # Calculamos la distancia entre centros
        dx = jugador_centro_x - robot_centro_x
        dy = jugador_centro_y - robot_centro_y
        distancia =  (dx * dx + dy * dy) ** 0.5

        # Usando un valor absoluto para rango
        rango_real = self.rango_deteccion
        
        if distancia <= rango_real:
            return Estado.EXITO
        else:
            return Estado.FALLO

# Nodos de comportamiento específicos
class Perseguir(NodoBase):
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Marca el estado actual del robot
        robot.estado_actual = "persecución"

        # Utiliza A* para perseguir al jugador
        robot.mover_hacia_jugador(jugador_x, jugador_y, otros_robots, laberinto)

        # Siempre devuelve EJECUTANDO para que siga persiguiendo
        return Estado.EJECUTANDO

class Patrullar(NodoBase):
    """Comportamiento de patrulla"""
    def __init__(self):
        super().__init__()
        self.puntos_patrulla = None
        self.punto_actual = 0
        self.margen_llegada = 5

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Marca el estado actual del robot
        robot.estado_actual = "patrulla"

        # En este caso usa los puntos de patrulla ya definidos en el robot
        robot.mover_en_patrulla(otros_robots)

        # Siempre devuelve EJECUTANDO para que siga patrullando
        return Estado.EJECUTANDO