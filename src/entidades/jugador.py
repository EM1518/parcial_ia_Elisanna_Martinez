import pygame
import math
from src.constantes import *
from src.entidades.bala import Bala

#Clase para el jugador
class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = ANCHO_JUGADOR
        self.alto = ALTO_JUGADOR
        self.velocidad = 5
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = RETRASO_DISPARO_JUGADOR # Frames de delay
        self.color = VERDE
        self.dx = 0
        self.dy = 0

    def mover(self, dx, dy):
        """
        Guarda la dirección del movimiento para ser aplicada en actualizar()
        """
        self.dx = dx
        self.dy = dy

    def retroceder(self):
        """
        Retroceder a la última posición válida después de una colisión
        """
        self.x = self.ultima_x
        self.y = self.ultima_y
        self.rectangulo.x = round(self.x)
        self.rectangulo.y = round(self.y)

    def disparar(self, direccion_x, direccion_y):
        if self.tiempo_recarga <= 0:
            bala_x = self.x + self.ancho // 2 - 2.5
            bala_y = self.y + self.alto // 2 - 2.5

            # Normalizar la dirección
            length = math.sqrt(direccion_x ** 2 + direccion_y ** 2)
            if length != 0:
                self.tiempo_recarga -= 1
                direccion_x /= length
                direccion_y /= length
    
            self.balas.append(Bala(bala_x, bala_y, direccion_x, direccion_y))
            self.tiempo_recarga = self.retraso_disparo

    def actualizar(self):

        """
        Actualiza la posición y estado del jugador
        """
        # Guardar posición anterior para colisiones
        self.ultima_x = self.x
        self.ultima_y = self.y

        # Calcular nueva posición basada en dx y dy
        if self.dx != 0 or self.dy != 0:
            # Normalizar el movimiento diagonal
            if self.dx != 0 and self.dy != 0:
                self.dx *= 0.7071  # 1/√2
                self.dy *= 0.7071

            # Aplicar velocidad
            self.x += self.dx * self.velocidad
            self.y += self.dy * self.velocidad

            # Mantener dentro de los límites de la pantalla
            self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ancho))
            self.y = max(0, min(self.y, ALTO_PANTALLA - self.alto))

            # Actualizar el rectángulo de colisión
            self.cuadrado.x = round(self.x)
            self.cuadrado.y = round(self.y)

        # Actualizar cooldown de disparo
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1

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