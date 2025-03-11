
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
    def __init__(self, rango_deteccion=250):
        super().__init__()
        self.rango_deteccion = rango_deteccion

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Si se fuerza patrulla, siempre falla
        if forzar_patrulla:
            return Estado.FALLO

        # Calcula posiciones centrales
        robot_centro_x = robot.x + robot.ancho / 2
        robot_centro_y = robot.y + robot.alto / 2
        jugador_centro_x = jugador_x + robot.ancho / 2
        jugador_centro_y = jugador_y + robot.alto / 2

        # Calcula la distancia entre centros
        dx = jugador_centro_x - robot_centro_x
        dy = jugador_centro_y - robot_centro_y
        distancia =  (dx * dx + dy * dy) ** 0.5

        if distancia <= self.rango_deteccion:
            # Establecer el estado del robot
            robot.estado_actual = "persecución"
            return Estado.EXITO
        else:
            return Estado.FALLO

# Nodos de comportamiento
class Perseguir(NodoBase):
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Utiliza A* para perseguir al jugador
        robot.mover_hacia_jugador(jugador_x, jugador_y, otros_robots, laberinto)

        # Siempre devuelve EJECUTANDO para que siga persiguiendo
        return Estado.EJECUTANDO

class DisparoConProbabilidad(NodoBase):
     def __init__(self, probabilidad=0.05):
        super().__init__()
        self.probabilidad = probabilidad
     def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        if robot.puede_disparar and robot.tiempo_recarga <= 0:
            aleatorio = (robot.x * robot.y + robot.tiempo_recarga) % 100 / 100
            if aleatorio < self.probabilidad:
                robot.disparar_a_jugador(jugador_x, jugador_y)
                return Estado.EXITO
        return Estado.EJECUTANDO

class Patrullar(NodoBase):
    """Comportamiento de patrulla"""
    def __init__(self):
        super().__init__()

    def ejecutar(self, robot, jugador_x, jugador_y, otros_robots, laberinto=None, forzar_patrulla=False):
        # Primero verifica si hay puntos de patrulla, si no, se generan
        if not robot.puntos_patrulla or len(robot.puntos_patrulla) < 2:
            self.generar_puntos_patrulla(robot, laberinto)

        # Marca el estado actual del robot
        robot.estado_actual = "patrulla"

        # Si no tiene suficientes puntos, no puede patrullar
        if len(robot.puntos_patrulla) < 2:
            return Estado.FALLO

        # Determinar el punto objetivo actual
        punto_actual = robot.puntos_patrulla[robot.punto_patrulla_actual]

        # Verificar si ha llegado al punto
        dx = punto_actual[0] - robot.x
        dy = punto_actual[1] - robot.y
        distancia = (dx * dx + dy * dy) ** 0.5

        # Si esta cerca del punto actual, moverse al siguiente
        if distancia < 10:
            # Actualizar el índice de punto de patrulla
            robot.punto_patrulla_actual = (robot.punto_patrulla_actual + 1) % len(robot.puntos_patrulla)
            # Actualizar la ruta para el nuevo destino
            robot.ruta_actual = []  # Limpiar ruta anterior
            return Estado.EJECUTANDO

        # Calcular dirección hacia el punto
        if distancia > 0:
            dx = dx / distancia
            dy = dy / distancia
        else:
            dx, dy = 0, 0

        # Aplicar el movimiento directamente
        nueva_x = robot.x + dx * robot.velocidad
        nueva_y = robot.y + dy * robot.velocidad

        # Mantener dentro de los límites
        nueva_x = max(0, min(nueva_x, 800 - robot.ancho))
        nueva_y = max(0, min(nueva_y, 600 - robot.alto))

        # Guardar posición anterior
        x_anterior = robot.x
        y_anterior = robot.y

        # Actualizar posición
        robot.x = nueva_x
        robot.y = nueva_y
        robot.cuadrado.x = nueva_x
        robot.cuadrado.y = nueva_y

        # Verificar colisión con paredes
        if laberinto and laberinto.verificar_colision(robot.cuadrado):
            # Si colisiona, volver a la posición anterior
            robot.x = x_anterior
            robot.y = y_anterior
            robot.cuadrado.x = x_anterior
            robot.cuadrado.y = y_anterior
            # Cambiar al siguiente punto si hay colisión
            robot.punto_patrulla_actual = (robot.punto_patrulla_actual + 1) % len(robot.puntos_patrulla)
        return Estado.EJECUTANDO

    def generar_puntos_patrulla(self, robot, laberinto):
        """Genera puntos de patrulla seguros para el robot"""
        # Limpiar puntos existentes
        robot.puntos_patrulla = []

        # Siempre añadir la posición actual como punto inicial
        robot.puntos_patrulla.append((robot.x, robot.y))

        # Intentar añadir solo 2 puntos más en direcciones simples
        distancia = 50

        # Direcciones cardinales
        direcciones = [
            (distancia, 0),  # Derecha
            (-distancia, 0),  # Izquierda
            (0, distancia),  # Abajo
            (0, -distancia)  # Arriba
        ]

        # Probar cada dirección
        for dx, dy in direcciones:
            x = robot.x + dx
            y = robot.y + dy

            # Mantener dentro de los límites de la pantalla
            x = max(20, min(x, 800 - 20))
            y = max(20, min(y, 600 - 20))

            # Verificar que no colisione con paredes
            from src.constantes import ANCHO_JUGADOR, ALTO_JUGADOR
            temp_rect = robot.cuadrado.__class__(x - ANCHO_JUGADOR / 2, y - ALTO_JUGADOR / 2, ANCHO_JUGADOR,
                                                   ALTO_JUGADOR)
            if not laberinto or not laberinto.verificar_colision(temp_rect):
                robot.puntos_patrulla.append((x, y))

            # Limitar a solo 2 puntos adicionales
            if len(robot.puntos_patrulla) >= 3:
                break

        # Si no se encontró ningún punto adicional, añadir uno muy cercano
        if len(robot.puntos_patrulla) < 2:
            robot.puntos_patrulla.append((robot.x + 10, robot.y))

        # Reiniciar el índice de patrulla
        robot.punto_patrulla_actual = 0