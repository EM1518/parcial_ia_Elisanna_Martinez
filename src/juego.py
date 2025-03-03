import pygame
import random
from src.constantes import *
from src.entidades.jugador import Jugador
from src.entidades.robot import Robot
from src.utilidades.colisiones import detectar_colision_entidades, detectar_colision_balas_entidad

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Berzerk")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.jugando = True

        #crear jugador
        self.jugador = Jugador(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
       
        #crear robots
        self.robots = []
        self.crear_robot(3) #crear con 3 robots

    def crear_robot(self, cantidad):
        #Área donde apareceran los robots
        area_x = ANCHO_PANTALLA - 200
        area_y = 100 

        for i in range(cantidad):
            #crear robots en formación
            x = area_x + (i * 50)
            y = area_y

            # Asegurarse de que no se salgan de la pantalla
            x = min(x, ANCHO_PANTALLA - ANCHO_JUGADOR)
            self.robots.append(Robot(x, y))

    def verificar_colisiones(self):
        # Verificar colisiones entre balas del jugador y robots
        for robot in self.robots[:]:  # Usamos [:] para poder modificar la lista durante la iteración
            if detectar_colision_balas_entidad(self.jugador.balas, robot):
                self.robots.remove(robot)  # Eliminar robot si es golpeado

        # Verificar colisiones entre balas de robots y jugador
        for robot in self.robots:
            if detectar_colision_balas_entidad(robot.balas, self.jugador):
                self.jugando = False  # El jugador pierde si es golpeado
                return

        # Verificar colisiones directas entre jugador y robots
        for robot in self.robots:
            if detectar_colision_entidades(self.jugador, robot):
                self.jugando = False
                return

    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
        
        if not self.jugando:
            return

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
        if not self.jugando:
            return

        self.jugador.actualizar()

        # Actualizar robots
        for robot in self.robots:
            robot.actualizar(self.jugador.x, self.jugador.y)

        # Verificar colisiones
        self.verificar_colisiones()

        # Verificar victoria
        if len(self.robots) == 0:
            print('Has ganado')
            self.jugando  = False


    def dibujar(self):
        self.pantalla.fill(NEGRO)

        if self.jugando:
            self.jugador.dibujar(self.pantalla)
            # Dibujar robots
            for robot in self.robots:
                robot.dibujar(self.pantalla)
        else:
            # Mostrar mensaje de fin de juego
            fuente = pygame.font.Font(None, 74)
            texto = "¡GAME OVER!"
            if len(self.robots) == 0:
                texto = "¡VICTORIA!"
            superficie_texto = fuente.render(texto, True, BLANCO)
            rect_texto = superficie_texto.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/2))
            self.pantalla.blit(superficie_texto, rect_texto)
        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        pygame.quit()

