import pygame
import math
from src.constantes import *
from src.entidades.bala import Bala

#Clase para el jugador
class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 32
        self.alto = 32
        self.velocidad = 5
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = 10 # 10 frames de delay
    
    def mover(self, dx, dy):
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad
        # Mantener al jugador dentro de los límites de la pantalla
        self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ancho))
        self.y = max(0, min(self.y, ALTO_PANTALLA - self.alto))       
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

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
        # Actualizar cooldown de disparo
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1

        # Actualizar balas
        for bala in self.balas[:]:
            bala.actualizar()
            if bala.esta_fuera_pantalla():
                self.balas.remove(bala)
   
    def dibujar(self, surface):
        pygame.draw.rect(surface, ROJO, self.cuadrado)
        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(surface)