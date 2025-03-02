import pygame
from src.constantes import *

#Clase Bala
class Bala:
    def __init__(self, x, y, direccion_x, direccion_y):
        self.x = x
        self.y = y        
        self.ancho = 5
        self.alto = 5
        self.velocidad = 10
        self.direccion_x = direccion_x
        self.direccion_y = direccion_y
        self.forma = pygame.Rect(x, y, self.ancho, self.alto)

    def actualizar(self):
        self.x +=  self.direccion_x * self.velocidad
        self.y +=  self.direccion_y * self.velocidad   
        self.forma.x = self.x
        self.forma.y = self.y

    def dibujar(self, surface):
        pygame.draw.rect(surface, AMARILLO, self.forma)

    def esta_fuera_pantalla (self):
        return(self.x < 0 or self.x > ANCHO_PANTALLA or
               self.y < 0 or self.y > ALTO_PANTALLA )

