import pygame
import math
from src.constantes import *
from src.entidades.bala import Bala
from src.utilidades.astar import AEstrella
from src.utilidades.arbol_comportamiento import Selector, Secuencia, JugadorEnRango, Perseguir, Patrullar, Estado

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = ANCHO_JUGADOR #usar el mismo que el jugador
        self.alto = ALTO_JUGADOR
        self.velocidad = 1 #mas lento que el jugador
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.color = VERDE
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = 120 # mas lento que el jugador
        self.tiempo_antes_disparar = 180  # 3 segundos 
        self.puede_disparar = False
        self.velocidad_bala = 5 
        self.distancia_minima_robots = 60  # Distancia mínima que queremos mantener
        self.estado_actual = "patrulla"

        # Variables para A*
        self.navegador = AEstrella()
        self.ruta_actual = []
        self.direccion_actual_x = 0
        self.direccion_actual_y = 0

        # Variables de patrulla
        self.puntos_patrulla = [
            (x, y),  # Posición inicial
            (x + 75, y),  # Derecha
            (x + 75, y + 75),  # Abajo-derecha
            (x, y + 75),  # Abajo
        ]
        self.punto_patrulla_actual = 0

        # Árbol de comportamiento
        self.arbol_comportamiento = Selector([
            Secuencia([
                JugadorEnRango(150),
                Perseguir()
            ]),
            Patrullar()
        ])

    def mantener_distancia_robots(self, otros_robots):
        # Vector resultante de separación
        separacion_x = 0
        separacion_y = 0
        
        for otro_robot in otros_robots:
            if otro_robot != self:
                dx = self.x - otro_robot.x
                dy = self.y - otro_robot.y
                distancia = math.sqrt(dx * dx + dy * dy)
                
                # Si están muy cerca, calcular vector de separación
                if distancia < self.distancia_minima_robots and distancia > 0:
                    # Cuanto más cerca estén, más fuerte es la separación
                    fuerza = (self.distancia_minima_robots - distancia) / distancia
                    separacion_x += dx * fuerza
                    separacion_y += dy * fuerza

        return separacion_x, separacion_y

    def actualizar_direccion(self, jugador_x, jugador_y, otros_robots):
        # Obtener nueva ruta
        nueva_ruta = self.navegador.encontrar_ruta(
            int(self.x), int(self.y),
            int(jugador_x), int(jugador_y)
        )
        
        if nueva_ruta and len(nueva_ruta) > 1:

            # Guardar la ruta para visualización
            self.ruta_actual = nueva_ruta

            # Calcular la dirección basada en el primer punto de la nueva ruta
            siguiente_punto = nueva_ruta[1]  # Usar el segundo punto para evitar giros bruscos
            dx = siguiente_punto[0] - self.x
            dy = siguiente_punto[1] - self.y      
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia != 0:
                self.direccion_actual_x = dx / distancia
                self.direccion_actual_y = dy / distancia

            # Obtener vector de separación de otros robots
            sep_x, sep_y = self.mantener_distancia_robots(otros_robots)
            
            # Combinar la dirección hacia el objetivo con la separación
            if sep_x != 0 or sep_y != 0:
                factor_separacion = 0.5  # Ajusta la influencia de la separación
                self.direccion_actual_x += sep_x * factor_separacion
                self.direccion_actual_y += sep_y * factor_separacion
                
                # Normalizar la dirección resultante
                magnitud = math.sqrt(self.direccion_actual_x**2 + self.direccion_actual_y**2)
                if magnitud != 0:
                    self.direccion_actual_x /= magnitud
                    self.direccion_actual_y /= magnitud

    def mover_hacia_objetivo(self, objetivo_x, objetivo_y, otros_robots):
        dx = objetivo_x - self.x
        dy = objetivo_y - self.y
        distancia = math.sqrt(dx * dx + dy * dy)
        if distancia != 0:
            # Normalizar el vector de dirección
            dx = dx / distancia
            dy = dy / distancia
            
            # Aplicar velocidad
            nueva_x = self.x + dx * self.velocidad
            nueva_y = self.y + dy * self.velocidad
            
            # Mantener dentro de los límites
            nueva_x = max(0, min(nueva_x, ANCHO_PANTALLA - self.ancho))
            nueva_y = max(0, min(nueva_y, ALTO_PANTALLA - self.alto))
            
            # Aplicar separación de otros robots
            sep_x, sep_y = self.mantener_distancia_robots(otros_robots)
            if sep_x != 0 or sep_y != 0:
                nueva_x += sep_x * 0.5
                nueva_y += sep_y * 0.5
            
            # Actualizar posición
            self.x = nueva_x
            self.y = nueva_y
            self.cuadrado.x = self.x
            self.cuadrado.y = self.y

    def mover_hacia_jugador(self, jugador_x, jugador_y, otros_robots):
        # Actualizar dirección basada en la nueva posición del jugador
        self.mover_hacia_objetivo(jugador_x, jugador_y, otros_robots)
        
    def disparar_a_jugador(self, jugador_x, jugador_y):
        if not self.puede_disparar  or self.tiempo_recarga > 0:
            return        
        
        if self.tiempo_recarga <= 0:
            # Calcular la dirección hacia el jugador
            dx = jugador_x - self.x
            dy = jugador_y - self.y

            # Normalizar la dirección
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia != 0:
                dx /= distancia
                dy /= distancia

                # crear la bala desde el centro del robot
                bala_x = self.x + self.ancho // 2 - ANCHO_BALA // 2
                bala_y = self.y + self.alto // 2 - ALTO_BALA // 2

                # Crear bala con velocidad personalizada
                bala = Bala(bala_x, bala_y, dx, dy)
                bala.velocidad = self.velocidad_bala  # Sobreescribir la velocidad de la bala
                self.balas.append(bala)
                self.tiempo_recarga = self.retraso_disparo
            
    def actualizar(self, jugador_x, jugador_y, otros_robots=None):

        # Reduce el tiempo de espera antes de que el robot pueda disparar
        if self.tiempo_antes_disparar > 0:
            self.tiempo_antes_disparar -= 1
            if self.tiempo_antes_disparar <= 0:
                self.puede_disparar = True       

        # Actualizar tiempo de recarga
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1
        
        # Calcular distancia al jugador para determinar comportamiento
        dx = jugador_x - self.x
        dy = jugador_y - self.y
        distancia_jugador = math.sqrt(dx * dx + dy * dy)

        if distancia_jugador <= 150:  # Rango de detección
            self.estado_actual = "persecución"
            self.mover_hacia_jugador(jugador_x, jugador_y, otros_robots)
            if self.puede_disparar:
                self.disparar_a_jugador(jugador_x, jugador_y)
        else:
            self.estado_actual = "patrulla"
            # Obtener punto actual de patrulla
            punto = self.puntos_patrulla[self.punto_patrulla_actual]
            # Calcular distancia al punto de patrulla
            dx_patrulla = punto[0] - self.x
            dy_patrulla = punto[1] - self.y
            dist_patrulla = math.sqrt(dx_patrulla * dx_patrulla + dy_patrulla * dy_patrulla)
            
            # Si llegamos al punto, ir al siguiente
            if dist_patrulla < 5:  # 5 píxeles de margen
                self.punto_patrulla_actual = (self.punto_patrulla_actual + 1) % len(self.puntos_patrulla)
            else:
                self.mover_hacia_objetivo(punto[0], punto[1], otros_robots)

        # Actualizar balas
        for bala in self.balas[:]:
            bala.actualizar()
            if bala.esta_fuera_pantalla():
                self.balas.remove(bala)


    def dibujar(self, surface):
        # Dibujar puntos de patrulla y líneas de conexión si está patrullando
        if self.estado_actual == "patrulla":
            for i, punto in enumerate(self.puntos_patrulla):
                # Dibujar punto
                pygame.draw.circle(surface, (255, 0, 0), (int(punto[0]), int(punto[1])), 3)
                # Dibujar línea al siguiente punto
                siguiente = self.puntos_patrulla[(i + 1) % len(self.puntos_patrulla)]
                pygame.draw.line(surface, (255, 0, 0), punto, siguiente, 1)

        # Dibujar la ruta (para depuración)
        if self.ruta_actual:
            for i in range(len(self.ruta_actual) - 1):
                pygame.draw.line(surface, (255, 0, 0), 
                               self.ruta_actual[i], 
                               self.ruta_actual[i + 1], 1)

        pygame.draw.rect(surface, self.color, self.cuadrado)
        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(surface)
