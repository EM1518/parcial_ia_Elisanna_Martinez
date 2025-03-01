import pygame
import sys

#Iniciando Pygame
pygame.init()

ALTO_PANTALLA = 600
ANCHO_PANTALLA = 800

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Berzerk")

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

# Bucle principal 
ejecutando = True
while ejecutando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
