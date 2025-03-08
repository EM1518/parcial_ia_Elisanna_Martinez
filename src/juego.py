import pygame
import random
import math
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

        # Estado del juego
        self.reiniciar_juego()


    def reiniciar_juego(self):
        #crear jugador
        self.jugador = Jugador(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
       
        #crear robots
        self.robots = []
        self.crear_robot(3) #crear con 3 robots

        # Estado de juego
        self.jugando = True
        self.victoria = False

    def verificar_distancia_minima(self, x, y, distancia_minima=100):
        """Verifica si un punto está a una distancia mínima de todos los robots existentes"""
        for robot in self.robots:
            dx = x - robot.x
            dy = y - robot.y
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia < distancia_minima:
                return False
        return True
    
    def crear_robot(self, cantidad):
        for _ in range(cantidad):
            # Intentar crear robot en posición válida
            intentos = 0
            while intentos < 100:  # Límite de intentos para evitar bucle infinito
                x = random.randint(0, ANCHO_PANTALLA - ANCHO_JUGADOR)
                y = random.randint(0, ALTO_PANTALLA - ALTO_JUGADOR)
                
                # Verificar distancia mínima con otros robots
                if self.verificar_distancia_minima(x, y):
                    self.robots.append(Robot(x, y))
                    break
                
                intentos += 1

    def verificar_colisiones_robots(self):
        # Para cada robot, verificar colisión con otros robots
        for i, robot in enumerate(self.robots):
            for otro_robot in self.robots[i+1:]:
                if detectar_colision_entidades(robot, otro_robot):
                    # Separar robots
                    dx = robot.x - otro_robot.x
                    dy = robot.y - otro_robot.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist != 0:
                        # Normalizar y aplicar una separación mayor
                        dx = dx / dist
                        dy = dy / dist
                        distancia_separacion = 50  # Aumentada de 2 a 50
                        
                        # Mover ambos robots en direcciones opuestas
                        robot.x += dx * distancia_separacion / 2
                        robot.y += dy * distancia_separacion / 2
                        otro_robot.x -= dx * distancia_separacion / 2
                        otro_robot.y -= dy * distancia_separacion / 2
                        
                        # Mantener dentro de los límites de la pantalla
                        robot.x = max(0, min(robot.x, ANCHO_PANTALLA - robot.ancho))
                        robot.y = max(0, min(robot.y, ALTO_PANTALLA - robot.alto))
                        otro_robot.x = max(0, min(otro_robot.x, ANCHO_PANTALLA - otro_robot.ancho))
                        otro_robot.y = max(0, min(otro_robot.y, ALTO_PANTALLA - otro_robot.alto))
                        
                        # Actualizar cuadrados
                        robot.cuadrado.x = robot.x
                        robot.cuadrado.y = robot.y
                        otro_robot.cuadrado.x = otro_robot.x
                        otro_robot.cuadrado.y = otro_robot.y

    def verificar_colisiones(self):
        # Verificar colisiones entre balas del jugador y robots
        for robot in self.robots[:]:  # Usamos [:] para poder modificar la lista durante la iteración
            if detectar_colision_balas_entidad(self.jugador.balas, robot):
                self.robots.remove(robot)  # Eliminar robot si es golpeado

        # Verificar colisiones entre balas de robots y jugador
        for robot in self.robots:
            if detectar_colision_balas_entidad(robot.balas, self.jugador):
                self.jugando = False  # El jugador pierde si es golpeado
                self.victoria = False
                return

        # Verificar colisiones directas entre jugador y robots
        for robot in self.robots:
            if detectar_colision_entidades(self.jugador, robot):
                self.jugando = False
                self.victoria = False
                return

        # Verificar victoria
        if len(self.robots) == 0:
            self.jugando = False
            self.victoria = True
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and not self.jugando:
                    self.reiniciar_juego()
        
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
            robot.actualizar(self.jugador.x, self.jugador.y, self.robots)

        # Verificar colisiones
        self.verificar_colisiones()
        self.verificar_colisiones_robots()

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

            # Mostrar mensaje de reinicio
            fuente_pequena = pygame.font.Font(None, 36)
            texto_reinicio = "Presiona R para jugar de nuevo"
            superficie_reinicio = fuente_pequena.render(texto_reinicio, True, BLANCO)
            rect_reinicio = superficie_reinicio.get_rect(center=(ANCHO_PANTALLA/2, ALTO_PANTALLA/2 + 50))
            self.pantalla.blit(superficie_reinicio, rect_reinicio)

        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        pygame.quit()

