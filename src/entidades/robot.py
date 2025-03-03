import pygame
import math
from src.constantes import *
from src.entidades.bala import Bala


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = ANCHO_JUGADOR #usar el mismo que el jugador
        self.alto = ALTO_JUGADOR
        self.velocidad = 2 #mas lento que el jugador
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.color = VERDE
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = 60 # mas lento que el jugador

    def mover_hacia_jugador(self, jugador_x, jugadot_y):

        # Calcular la dirección hacia el jugador
        dx = jugador_x - self.x
        dy = jugadot_y - self.y

        # Normalizar la dirección
        distancia = math.sqrt(dx * dx + dy * dy)
        if distancia != 0:
            dx /= distancia
            dy /= distancia

        # Mover el robot
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad

        #Actualizar el cuadrado
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

    def disparar_a_jugador(self, jugador_x, jugador_y):
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

            self.balas.append(Bala(bala_x, bala_y, dx, dy))
            self.tiempo_recarga = self.retraso_disparo

    def actualizar(self, jugador_x, jugador_y):
        # Actualizar tiempo de recarga
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1
        
        #mover hacia el jugador
        self.mover_hacia_jugador(jugador_x, jugador_y)

        #Intentar disparar
        self.disparar_a_jugador(jugador_x, jugador_y)

        # Actualizar balas
        for bala in self.balas[:]:
            bala.actualizar()
            if bala.esta_fuera_pantalla():
                self.balas.remove(bala)


    def dibujar(self, surface):
        pygame.draw.rect(surface, self.color, self.cuadrado)
        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(surface)
