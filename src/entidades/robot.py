import pygame
import math
import os
import random
from src.constantes import *
from src.entidades.bala import Bala
from src.utilidades.astar import AEstrella
from src.utilidades.arbol_comportamiento import Selector, Secuencia, JugadorEnRango, Perseguir, Patrullar, Estado, DisparoConProbabilidad

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
        self.velocidad_bala = VELOCIDAD_BALA
        self.distancia_minima_robots = 60
        self.estado_actual = "patrulla"

        # Variables para A*
        self.navegador = AEstrella()
        self.ruta_actual = []

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
        disparar = DisparoConProbabilidad(0.05)

        # Secuencia: primero verificar si el jugador está en rango, luego perseguirlo, y posiblemente disparar
        secuencia_perseguir = Secuencia([jugador_en_rango, perseguir, disparar])

        # Nodo de patrulla
        patrullar = Patrullar()

        # Selector principal: perseguir si el jugador está en rango, si no, patrullar
        self.arbol_comportamiento = Selector([secuencia_perseguir, patrullar])

    def aplicar_movimiento(self, direccion_x, direccion_y, laberinto=None):
        """Aplica movimiento en la dirección dada, respetando colisiones"""

        # Calcular nueva posición
        nueva_x = self.x + direccion_x * self.velocidad
        nueva_y = self.y + direccion_y * self.velocidad

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
            return False
        return True

    def mover_hacia_jugador(self, jugador_x, jugador_y, otros_robots, laberinto=None):
        """Utiliza el A* para moverse hacia el jugador"""
        # Inicializar variables de seguimiento si no existen
        try:
            self.ultima_pos_jugador_x
            self.ultima_pos_jugador_y
            self.contador_frames
        except AttributeError:
            # Si no existen, se crean
            self.ultima_pos_jugador_x = jugador_x
            self.ultima_pos_jugador_y = jugador_y
            self.contador_frames = 0

        # Incrementar contador de frames
        self.contador_frames += 1

        # Calcular si el jugador se ha movido significativamente
        distancia_jugador = ((jugador_x - self.ultima_pos_jugador_x) ** 2 +
                             (jugador_y - self.ultima_pos_jugador_y) ** 2)
        jugador_movido = distancia_jugador > 900  # 30 píxeles cuadrados

        # Verificar si existe la ruta_actual
        tiene_ruta = True
        try:
            if not self.ruta_actual or len(self.ruta_actual) <= 1:
                tiene_ruta = False
        except AttributeError:
            tiene_ruta = False
            self.ruta_actual = []

        # Determinar si necesitamos recalcular la ruta
        recalcular_ruta = (
                not tiene_ruta or
                self.contador_frames % 30 == 0 or  # Recalcular cada 30 frames (aprox. 0.5 segundos)
                jugador_movido
        )

        if recalcular_ruta:
            nueva_ruta = self.navegador.encontrar_ruta(
                int(self.x), int(self.y),
                int(jugador_x), int(jugador_y)
            )

            # Guardar la ruta y actualizar posición del jugador
            if nueva_ruta and len(nueva_ruta) > 1:
                self.ruta_actual = nueva_ruta
                self.ultima_pos_jugador_x = jugador_x
                self.ultima_pos_jugador_y = jugador_y

        # Si no hay ruta válida, no podemos movernos
        if not self.ruta_actual or len(self.ruta_actual) <= 1:
            return False

        # Obtener dirección hacia el siguiente punto
        siguiente_punto = self.ruta_actual[1]
        dx = siguiente_punto[0] - self.x
        dy = siguiente_punto[1] - self.y
        distancia = (dx * dx + dy * dy) ** 0.5

        # Si esta cerca del punto, avanzar al siguiente
        if distancia < 10:
            self.ruta_actual.pop(0)
            return True

        # Normalizar dirección
        if distancia > 0:
            dx = dx / distancia
            dy = dy / distancia

        # Aplicar vector de separación de otros robots
        sep_x, sep_y = self.mantener_distancia_robots(otros_robots)

        # Combinar dirección de movimiento con separación
        peso_separacion = 0.4  # 40% de influencia para la separación
        direccion_x = dx * (1 - peso_separacion) + sep_x * peso_separacion
        direccion_y = dy * (1 - peso_separacion) + sep_y * peso_separacion

        # Renormalizar
        magnitud = (direccion_x * direccion_x + direccion_y * direccion_y) ** 0.5
        if magnitud > 0:
            direccion_x /= magnitud
            direccion_y /= magnitud

        # Aplicar el movimiento con la dirección combinada
        return self.aplicar_movimiento(direccion_x, direccion_y, laberinto)

    def mantener_distancia_robots(self, otros_robots):
        """
        Calcula un vector de separación para mantener distancia con otros robots
        """
        # Vector resultante de separación
        separacion_x = 0
        separacion_y = 0

        for otro_robot in otros_robots:
            if otro_robot != self:
                dx = self.x - otro_robot.x
                dy = self.y - otro_robot.y
                distancia_cuadrado = dx * dx + dy * dy
                distancia = distancia_cuadrado ** 0.5

                # Si están muy cerca, calcular vector de separación
                if distancia < self.distancia_minima_robots and distancia > 0:
                    # Cuanto más cerca estén, más fuerte es la separación
                    fuerza = (self.distancia_minima_robots - distancia) / distancia
                    separacion_x += dx * fuerza
                    separacion_y += dy * fuerza

        return separacion_x, separacion_y

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
        bala.velocidad = VELOCIDAD_BALA
        self.balas.append(bala)
        self.tiempo_recarga = self.retraso_disparo
        return True

    def actualizar(self, jugador_x, jugador_y, otros_robots, forzar_patrulla=False, laberinto=None):
        """
        Actualiza el estado del robot utilizando el árbol de comportamiento
        """
        # Gestión de tiempos
        # Reduce el tiempo de espera antes de que el robot pueda disparar
        if self.tiempo_antes_disparar > 0:
            self.tiempo_antes_disparar -= 1
        if self.tiempo_antes_disparar <= 0:
            self.puede_disparar = True
        # Actualizar tiempo de recarga
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1

         # Asegurar que el navegador tenga información actualizada de obstáculos
        if not self.obstaculos_actualizados and laberinto:
            self.navegador.actualizar_obstaculos(laberinto.obtener_paredes_para_astar())
            self.obstaculos_actualizados = True

        # Ejecutar el árbol de comportamiento para determinar acciones
        resultado = self.arbol_comportamiento.ejecutar(self, jugador_x, jugador_y, otros_robots, laberinto,
                                                       forzar_patrulla)

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

        # # Dibujar puntos de patrulla y líneas de conexión si está patrullando
        # if self.estado_actual == "patrulla":
        #     for i, punto in enumerate(self.puntos_patrulla):
        #         # Dibujar punto
        #         pygame.draw.circle(surface, (255, 0, 0), (int(punto[0]), int(punto[1])), 3)
        #
        #         # Dibujar línea al siguiente punto
        #         siguiente = self.puntos_patrulla[(i + 1) % len(self.puntos_patrulla)]
        #         pygame.draw.line(surface, (255, 0, 0), punto, siguiente, 1)
        #
        # # Dibujar la ruta (para depuración)
        # if self.ruta_actual and self.estado_actual == "persecución":
        #     for i in range(len(self.ruta_actual) - 1):
        #         pygame.draw.line(surface, (255, 0, 0),
        #                        self.ruta_actual[i],
        #                        self.ruta_actual[i + 1], 1)


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