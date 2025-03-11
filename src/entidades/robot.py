import pygame
import math
import os
import random
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
        self.velocidad = 1
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.color = AMARILLO
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = 120
        self.tiempo_antes_disparar = 180  # 3 segundos 
        self.puede_disparar = False
        self.velocidad_bala = 5 
        self.distancia_minima_robots = 60
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

        # Configuración del árbol de comportamiento
        self.configurar_arbol_comportamiento()
        self.obstaculos_actualizados = False

        # Cargar sprites
        self.cargar_sprites()

    def configurar_arbol_comportamiento(self):
        """
        Configura el árbol de comportamiento del robot
        """
        # Crea los nodos de comportamiento
        jugador_en_rango = JugadorEnRango(250)  # Detecta al jugador en un rango de X píxeles
        perseguir = Perseguir()  # El robot persigue al jugador
        secuencia_perseguir = Secuencia([jugador_en_rango, perseguir])  # Secuencia: primero detectar, luego perseguir

        patrullar = Patrullar()  # El robot patrulla si no detecta al jugador

        # Selector principal: perseguir si el jugador está en rango, si no, patrullar
        self.arbol_comportamiento = Selector([secuencia_perseguir, patrullar])

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

    def mover_hacia_jugador(self, jugador_x, jugador_y, otros_robots, laberinto=None):
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
        else:
            # Si no hay ruta disponible, intentar rodear obstáculos
            self.rodear_obstaculos(jugador_x, jugador_y, laberinto)
            return

        # Aplicar el movimiento
        nueva_x = self.x + self.direccion_actual_x * self.velocidad
        nueva_y = self.y + self.direccion_actual_y * self.velocidad

        # Mantener dentro de los límites
        nueva_x = max(0, min(nueva_x, ANCHO_PANTALLA - self.ancho))
        nueva_y = max(0, min(nueva_y, ALTO_PANTALLA - self.alto))

        # Guardar posición anterior
        x_anterior = self.x
        y_anterior = self.y

        self.x = nueva_x
        self.y = nueva_y
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

        # Verificar colisión con paredes
        if laberinto and laberinto.verificar_colision(self.cuadrado):
            # Si colisiona, volver a la posición anterior
            self.x = x_anterior
            self.y = y_anterior
            self.cuadrado.x = self.x
            self.cuadrado.y = self.y

            # Intentar rodear obstáculos
            self.rodear_obstaculos(jugador_x, jugador_y, laberinto)

    def rodear_obstaculos(self, jugador_x, jugador_y, laberinto):
        """Intenta encontrar una ruta alternativa alrededor de obstáculos"""
        if not laberinto:
            return

        # Dirección hacia el jugador
        dx = jugador_x - self.x
        dy = jugador_y - self.y
        distancia = math.sqrt(dx * dx + dy * dy)

        if distancia != 0:
            dx /= distancia
            dy /= distancia

        # Intentar 8 direcciones posibles
        direcciones = [
            (1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1)
        ]

        # Ordenar direcciones según su alineación con la dirección al jugador
        # (para priorizar direcciones que vayan hacia el jugador)
        direcciones.sort(key=lambda d: (d[0] * dx + d[1] * dy), reverse=True)

        for dir_x, dir_y in direcciones:
            # Normalizar para que la diagonal no sea más rápida
            if dir_x != 0 and dir_y != 0:
                dir_x *= 0.7071  # cos(45°)
                dir_y *= 0.7071  # sin(45°)

            # Verificar si podemos movernos en esta dirección
            nueva_x = self.x + dir_x * self.velocidad * 2  # Mirar un poco más adelante
            nueva_y = self.y + dir_y * self.velocidad * 2

            temp_rect = pygame.Rect(nueva_x, nueva_y, self.ancho, self.alto)

            if not laberinto.verificar_colision(temp_rect):
                # Esta dirección es válida, intentar moverse
                self.x += dir_x * self.velocidad
                self.y += dir_y * self.velocidad

                # Mantener dentro de los límites
                self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ancho))
                self.y = max(0, min(self.y, ALTO_PANTALLA - self.alto))

                self.cuadrado.x = self.x
                self.cuadrado.y = self.y

                # Si todavía colisiona, revertir
                if laberinto.verificar_colision(self.cuadrado):
                    self.x -= dir_x * self.velocidad
                    self.y -= dir_y * self.velocidad
                    self.cuadrado.x = self.x
                    self.cuadrado.y = self.y
                else:
                    # Se encontró una dirección válida, salir
                    break

    def mover_en_patrulla(self, otros_robots, laberinto=None):
        # Si no hay puntos de patrulla válidos, crear nuevos puntos seguros
        if not self.puntos_patrulla or len(self.puntos_patrulla) < 2:
            self.generar_puntos_patrulla_seguros(laberinto)

        # Asegurarse de que tengamos al menos dos puntos
        if len(self.puntos_patrulla) < 2:
            return  # No moverse si no hay suficientes puntos

        # Determinar el punto objetivo actual
        punto_actual = self.puntos_patrulla[self.punto_patrulla_actual]
        
        # Calcular dirección al punto actual
        dx = punto_actual[0] - self.x
        dy = punto_actual[1] - self.y
        distancia = math.sqrt(dx * dx + dy * dy)

        # Si estamos cerca del punto actual, comenzar a moverse hacia el siguiente
        if distancia < 10:  # Aumentado el margen para un movimiento más fluido
            self.punto_patrulla_actual = (self.punto_patrulla_actual + 1) % len(self.puntos_patrulla)
            return

        if distancia != 0:
            # Normalizar vector de dirección
            dx = dx / distancia
            dy = dy / distancia

        # Aplicar movimiento continuo
        nueva_x = self.x + dx * self.velocidad
        nueva_y = self.y + dy * self.velocidad

        # Mantener dentro de los límites
        nueva_x = max(0, min(nueva_x, ANCHO_PANTALLA - self.ancho))
        nueva_y = max(0, min(nueva_y, ALTO_PANTALLA - self.alto))

        # Guardar posición anterior
        x_anterior = self.x
        y_anterior = self.y

        # Actualizar posición
        self.x = nueva_x
        self.y = nueva_y
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

        # Verificar colisión con paredes
        if laberinto and laberinto.verificar_colision(self.cuadrado):
            # Si colisiona, volver a la posición anterior
            self.x = x_anterior
            self.y = y_anterior
            self.cuadrado.x = self.x
            self.cuadrado.y = self.y

            # Intentar regenerar puntos de patrulla si colisiona frecuentemente
            self.punto_patrulla_actual = (self.punto_patrulla_actual + 1) % len(self.puntos_patrulla)

    def generar_puntos_patrulla_seguros(self, laberinto):
        """Genera puntos de patrulla y seguros que no colisionen con paredes"""
        if not laberinto:
            return

        # Limpiar puntos existentes
        self.puntos_patrulla = []

        # Siempre añadir la posición actual como punto inicial
        self.puntos_patrulla.append((self.x, self.y))

        #  añadir solo 2 puntos en direcciones simples: arriba/abajo y derecha/izquierda
        distancia = 50  # Usar una distancia fija y corta

        # Direcciones cardinales simplificadas
        direcciones = [
            (distancia, 0),  # Derecha
            (-distancia, 0),  # Izquierda
            (0, distancia),  # Abajo
            (0, -distancia)  # Arriba
        ]

        # Probar cada dirección
        for dx, dy in direcciones:
            x = self.x + dx
            y = self.y + dy

            # Mantener dentro de los límites de la pantalla
            x = max(20, min(x, ANCHO_PANTALLA - 20))
            y = max(20, min(y, ALTO_PANTALLA - 20))

            # Verificar que no colisione con paredes
            temp_rect = pygame.Rect(x - self.ancho / 2, y - self.alto / 2, self.ancho, self.alto)
            if not laberinto.verificar_colision(temp_rect):
                self.puntos_patrulla.append((x, y))
            # Limitar a solo 2 puntos adicionales
            if len(self.puntos_patrulla) >= 3:
                break

        # Si no se encontró ningún punto adicional, añadir uno muy cercano
        if len(self.puntos_patrulla) < 2:
            for d in range(10, 31, 10):  # Distancias cortas
                for angle in range(0, 360, 90):  # Direcciones cardinales
                    rad = math.radians(angle)
                    x = self.x + math.cos(rad) * d
                    y = self.y + math.sin(rad) * d

                    # Mantener dentro de los límites
                    x = max(20, min(x, ANCHO_PANTALLA - 20))
                    y = max(20, min(y, ALTO_PANTALLA - 20))

                    # Verificar que no colisione con paredes
                    temp_rect = pygame.Rect(x - self.ancho / 2, y - self.alto / 2, self.ancho, self.alto)
                    if not laberinto.verificar_colision(temp_rect):
                        self.puntos_patrulla.append((x, y))
                        break

                if len(self.puntos_patrulla) >= 2:
                    break

        # si solo tenemos un punto, duplicarlo para tener al menos dos
        if len(self.puntos_patrulla) == 1:
            self.puntos_patrulla.append(self.puntos_patrulla[0])

        # Reiniciar el índice de patrulla
        self.punto_patrulla_actual = 0

    # método para verificar si hay un camino válido sin obstáculos
    def verificar_camino(self, x1, y1, x2, y2, laberinto):
        """Verifica si hay un camino sin obstáculos entre dos puntos"""
        # Versión simplificada: verificar si la línea recta entre los puntos colisiona con paredes
        # Muestrear varios puntos a lo largo de la línea
        for t in range(1, 10):  # 9 puntos entre el inicio y el final
            t = t / 10.0
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            temp_rect = pygame.Rect(x - self.ancho / 2, y - self.alto / 2, self.ancho, self.alto)
            if laberinto.verificar_colision(temp_rect):
                return False  # Hay obstáculo en el camino

        return True  # No hay obstáculos en el camino

    def disparar_a_jugador(self, jugador_x, jugador_y):
        if not self.puede_disparar or self.tiempo_recarga > 0:
            return

        if self.usar_sprites:
            self.sprite_actual = 'disparando'

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
        bala.velocidad = VELOCIDAD_BALA  # Usar la constante para la velocidad de la bala
        self.balas.append(bala)
        self.tiempo_recarga = self.retraso_disparo
            
    def actualizar(self, jugador_x, jugador_y, otros_robots, forzar_patrulla=False, laberinto=None):

        # Gestión de tiempos
        # Reduce el tiempo de espera antes de que el robot pueda disparar
        if self.tiempo_antes_disparar > 0:
            self.tiempo_antes_disparar -= 1
        if self.tiempo_antes_disparar <= 0:
            self.puede_disparar = True

        # Actualizar tiempo de recarga
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1

        # Ejecutar el árbol de comportamiento para determinar acciones
        resultado = self.arbol_comportamiento.ejecutar(self, jugador_x, jugador_y, otros_robots, laberinto,
                                                       forzar_patrulla)

        # Hacer que los robots disparen cuando están persiguiendo
        if self.estado_actual == "persecución" and self.puede_disparar and self.tiempo_recarga <= 0:
        # Aumentamos la probabilidad para que disparen más
            if random.random() < 0.05:  # 5% de probabilidad, mayor que antes
                self.disparar_a_jugador(jugador_x, jugador_y)

        # Actualizar balas
        for bala in self.balas[:]:
            # Si la bala colisiona con una pared, eliminarla
            if laberinto and bala.actualizar(laberinto):
                self.balas.remove(bala)
            elif bala.esta_fuera_pantalla():
                self.balas.remove(bala)

        # Actualizar animación si hay sprites
        if self.usar_sprites:
            self.frame_contador += 1
            if self.frame_contador < 20:
                self.sprite_actual = 'movimiento1'
            elif self.frame_contador < 40:
                self.sprite_actual = 'movimiento2'
            else:
                self.frame_contador = 0

    def dibujar(self, surface):

        """Dibuja el robot y sus balas"""
        if self.usar_sprites:
            surface.blit(self.sprites[self.sprite_actual], self.cuadrado)
        else:
            pygame.draw.rect(surface, self.color, self.cuadrado)
        for bala in self.balas:
            bala.dibujar(surface)

        # Dibujar puntos de patrulla y líneas de conexión si está patrullando
        if self.estado_actual == "patrulla":
            for i, punto in enumerate(self.puntos_patrulla):
                # Dibujar punto
                pygame.draw.circle(surface, (255, 0, 0), (int(punto[0]), int(punto[1])), 3)

                # Dibujar línea al siguiente punto
                siguiente = self.puntos_patrulla[(i + 1) % len(self.puntos_patrulla)]
                pygame.draw.line(surface, (255, 0, 0), punto, siguiente, 1)

        # Dibujar la ruta (para depuración)
        if self.ruta_actual and self.estado_actual == "persecución":
            for i in range(len(self.ruta_actual) - 1):
                pygame.draw.line(surface, (255, 0, 0), 
                               self.ruta_actual[i], 
                               self.ruta_actual[i + 1], 1)


    def cargar_sprites(self):
        """Carga los sprites del robot"""
        self.sprites = {}
        try:
            self.sprites['estatico'] = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'imagenes', 'robots','robot_estatico.png')),
                                                              (self.ancho, self.alto))
            self.sprites['movimiento1'] = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'imagenes', 'robots', 'robot_movimiento1.png')),
                                                                 (self.ancho, self.alto))
            self.sprites['movimiento2'] = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'imagenes', 'robots', 'robot_movimiento2.png')),
                                                                 (self.ancho, self.alto))
            self.sprites['disparando'] = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'imagenes', 'robots', 'robot_disparando.png')),
                                                                (self.ancho, self.alto))
            self.sprites['explotando'] = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'imagenes', 'robots', 'robot_explotando.png')),
                                                                (self.ancho, self.alto))
            self.usar_sprites = True
        except Exception as e:
            print(f"Error al cargar sprites del robot: {e}")
            self.usar_sprites = False

        self.sprite_actual = 'estatico'
        self.frame_contador = 0