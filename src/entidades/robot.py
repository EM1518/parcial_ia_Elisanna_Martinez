import pygame
import math
from src.constantes import *

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = ANCHO_JUGADOR #usar el mismo que el jugador
        self.alto = ALTO_JUGADOR
        self.velocidad = 2 #mas lento que el jugador
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.color = VERDE

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

    
    def actualizar(self, jugador_x, jugador_y):
       #mover hacia el jugador
         self.mover_hacia_jugador(jugador_x, jugador_y)

    def dibujar(self, surface):
        pygame.draw.rect(surface, self.color, self.cuadrado)
