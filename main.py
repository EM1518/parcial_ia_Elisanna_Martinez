import pygame
import sys

#Iniciando Pygame
pygame.init()

# Configuración de la pantalla
ALTO_PANTALLA = 600
ANCHO_PANTALLA = 800
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Berzerk")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

#Clase para el jugador
class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 32
        self.alto = 32
        self.velocidad = 5
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
    
    def dibujar(self, surface):
        pygame.draw.rect(surface, ROJO, self.cuadrado)

jugador = Jugador(ANCHO_PANTALLA //2, ALTO_PANTALLA // 2)

# Bucle principal 
ejecutando = True
while ejecutando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
    
    #Dibujar al jugador
    jugador.dibujar(pantalla)

    #Actualizar la pantalla
    pygame.display.flip()
