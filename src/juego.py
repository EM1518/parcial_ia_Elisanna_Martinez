import pygame
from src.constantes import *
from src.entidades.jugador import Jugador

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Berzerk")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True

        #crear jugador
        self.jugador = Jugador(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
        
        # Teclas presionadas
        teclas = pygame.key.get_pressed()

        dx = teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]
        dy = teclas[pygame.K_DOWN] - teclas[pygame.K_UP]
        self.jugador.mover(dx, dy)

        #Sistema de disparo
        if teclas[pygame.K_w]: #Arriba
            self.jugador.disparar(0, -1) 
        if teclas[pygame.K_s]: #Abajo
            self.jugador.disparar(0, 1)
        if teclas[pygame.K_a]: #Izquierda
            self.jugador.disparar(-1, 0)
        if teclas[pygame.K_d]:  #Derecha
            self.jugador.disparar(1, 0)


    def actualizar(self):
        self.jugador.actualizar()

    def dibujar(self):
        self.pantalla.fill((0, 0, 0))
        self.jugador.dibujar(self.pantalla)
        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        pygame.quit()

