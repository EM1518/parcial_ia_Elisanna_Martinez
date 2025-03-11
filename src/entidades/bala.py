import pygame
from src.constantes import *

#Clase Bala
class Bala:
    def __init__(self, x, y, direccion_x, direccion_y):
        self.x = x
        self.y = y        
        self.ancho = ANCHO_BALA
        self.alto = ALTO_BALA
        self.velocidad = VELOCIDAD_BALA
        self.direccion_x = direccion_x
        self.direccion_y = direccion_y
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)

    def actualizar(self, laberinto=None):
        """
        Actualiza la posición de la bala y verifica colisiones con paredes
        """
        # Mover la bala
        self.x +=  self.direccion_x * self.velocidad
        self.y +=  self.direccion_y * self.velocidad   
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

        # Verificar colisión con paredes si se proporciona un laberinto
        if laberinto and laberinto.verificar_colision(self.cuadrado):
            return True  # Indicar que la bala colisionó

        return False  # Indicar que la bala no colisionó

    def dibujar(self, surface):
        pygame.draw.rect(surface, AMARILLO, self.cuadrado)

    def esta_fuera_pantalla (self):
        return(self.x < 0 or self.x > ANCHO_PANTALLA or
               self.y < 0 or self.y > ALTO_PANTALLA )

