import pygame
import sys
import math

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
AMARILLO = (255, 255, 0)
# Reloj para controlar los FPS
reloj = pygame.time.Clock()

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
        self.cooldown_disparo = 0
        self.delay_disparo = 10 # 10 frames de delay
    
    def mover(self, dx, dy):
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad
        # Mantener al jugador dentro de los límites de la pantalla
        self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ancho))
        self.y = max(0, min(self.x, ALTO_PANTALLA - self.alto))       
        self.cuadrado.x = self.x
        self.cuadrado.y = self.y

    def disparar(self, direccion_x, direccion_y):
        if self.cooldown_disparo <= 0:
            bala_x = self.x + self.ancho // 2 - 2.5
            bala_y = self.y + self.alto // 2 - 2.5

            # Normalizar la dirección
            length = math.sqrt(direccion_x ** 2 + direccion_y ** 2)
            if length != 0:
                self.cooldown_disparo -= 1
                direccion_x /= length
                direccion_y /= length
    
            self.balas.append(Bala(bala_x, bala_y, direccion_x, direccion_y))
            self.cooldown_disparo = self.delay_disparo

    def actualizar(self):
        # Actualizar cooldown de disparo
        if self.cooldown_disparo > 0:
            self.cooldown_disparo -= 1

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

# Crear al Jugador
jugador = Jugador(ANCHO_PANTALLA //2, ALTO_PANTALLA // 2)


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


    #Sistema de disparo
    if teclas[pygame.K_w]: #Arriba
        jugador.disparar(0, -1) 
    if teclas[pygame.K_s]: #Abajo
        jugador.disparar(0, 1)
    if teclas[pygame.K_a]: #Izquierda
        jugador.disparar(-1, 0)
    if teclas[pygame.K_d]:  #Derecha
        jugador.disparar(1, 0)

    # actualizar estado del jugador
    jugador.actualizar()

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
