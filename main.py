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
    
    def mover(self, dx, dy):
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad
        # Mantener al jugador dentro de los límites de la pantalla
        self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ancho))
        self.y = max(0, min(self.x, ALTO_PANTALLA - self.alto))       
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

    def dibujar(self, surface):
        pygame.draw.rect(surface, ROJO, self.cuadrado)

# Crear al Jugador
jugador = Jugador(ANCHO_PANTALLA //2, ALTO_PANTALLA // 2)

# Reloj para controlar los FPS
reloj = pygame.time.Clock()

# Bucle principal 
ejecutando = True
while ejecutando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
    
    # Teclas presionadas
    teclas = pygame.key.get_pressed()

    dx = teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]
    dy = teclas[pygame.K_DOWN] - teclas[pygame.K_UP]
    jugador.mover(dx, dy)

    #Limpiar la pantalla
    pantalla.fill(NEGRO)

    #Dibujar al jugador
    jugador.dibujar(pantalla)

    #Actualizar la pantalla
    pygame.display.flip()

    #Controlar la velcidad del juegp
    reloj.tick(60)


pygame.quit()
sys.exit()
