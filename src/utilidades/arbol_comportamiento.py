
def calcular_distancia(x1, y1, x2, y2):
    """Calcula la distancia euclidiana entre dos puntos sin usar math.sqrt"""
    dx = x2 - x1
    dy = y2 - y1

    # Aproximación rápida de raíz cuadrada usando iteraciones
    distancia_cuadrada = dx * dx + dy * dy

    # Método de aproximación de Newton-Raphson
    x = distancia_cuadrada  # Valor inicial
    for _ in range(5):  # 5 iteraciones es suficiente para buena precisión
        x = 0.5 * (x + distancia_cuadrada / x)

    return x


def normalizar_vector(dx, dy):
    """Normaliza un vector 2D sin usar math.sqrt"""
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
        distancia = calcular_distancia(0, 0, dx, dy)
        
        if distancia <= self.rango_deteccion:
            return Estado.EXITO
        else:
            return Estado.FALLO

# Nodos de comportamiento específicos
class Perseguir(NodoBase):
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        # Marca el estado actual del robot
        robot.estado_actual = "persecución"

        # Utiliza A* para perseguir al jugador
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
                (x_base, y_base),
                (x_base + offset, y_base),
                (x_base + offset, y_base + offset),
                (x_base, y_base + offset),
            ]

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots):
        # Marca el estado actual del robot
        robot.estado_actual = "patrulla"

        # En este caso usamos los puntos de patrulla ya definidos en el robot
        robot.mover_en_patrulla(otros_robots)
        return Estado.EJECUTANDO