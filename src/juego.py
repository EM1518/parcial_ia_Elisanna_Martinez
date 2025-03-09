import pygame
import random
import math
from src.constantes import *
from src.entidades.jugador import Jugador
from src.entidades.robot import Robot
from src.utilidades.colisiones import detectar_colision_entidades, detectar_colision_balas_entidad
from src.laberinto import Laberinto

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Berzerk")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True

        # Definir zona de inicio
        margen = 50
        tamano_zona = 150
        self.zona_inicio = pygame.Rect(
            margen, 
            ALTO_PANTALLA - margen - tamano_zona,
            tamano_zona,
            tamano_zona
        )

        # Inicializar el laberinto
        self.laberinto = Laberinto()

        # Estado del juego
        self.reiniciar_juego()

    def jugador_en_zona_inicio(self):
        return self.zona_inicio.colliderect(self.jugador.cuadrado)

    def reiniciar_juego(self):
       # Crear jugador en el centro de la zona de inicio
        self.jugador = Jugador(
            self.zona_inicio.centerx,
            self.zona_inicio.centery
        )
        # Cambiamos el color del jugador a verde 
        self.jugador.color = VERDE
       
        #crear robots
        self.robots = []
        self.crear_robot(6) #crear 6 robots

        # Estado de juego
        self.jugando = True
        self.victoria = False
        self.jugador_salio = False  # controlar si el jugador ya salió del cuadro seguro

 
    def crear_robot(self, cantidad):
        # Posiciones predefinidas para los robots 
        posiciones = [
            (600, 80),   # Arriba derecha
            (700, 80),   # Arriba derecha
            (500, 300),  # Centro derecha
            (600, 300),  # Centro derecha
            (500, 500),  # Abajo derecha
            (700, 500)   # Abajo derecha
        ]
        
        for i in range(min(cantidad, len(posiciones))):
            x, y = posiciones[i]
            nuevo_robot = Robot(x, y)
            # Establecemos rutas de patrulla relativas a su posición
            nuevo_robot.puntos_patrulla = [
                (x, y),  # Posición inicial
                (x + 50, y),  # Derecha
                (x + 50, y + 50),  # Abajo-derecha
                (x, y + 50),  # Abajo
            ]
            self.robots.append(nuevo_robot)

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

        # Verificar colisiones entre jugador y paredes
        if self.laberinto.verificar_colision(self.jugador.cuadrado):
            # Si el jugador colisiona con una pared pierde
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

        self.jugador.dx = dx
        self.jugador.dy = dy

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

        # Guardar posición anterior del jugador para verificar colisiones
        pos_anterior_x = self.jugador.x
        pos_anterior_y = self.jugador.y

        self.jugador.actualizar()

        # Verificar colisiones del jugador con las paredes después de actualizar
        if self.laberinto.verificar_colision(self.jugador.cuadrado):
            # Si hay colisión, pierde inmediatamente
            self.jugando = False
            self.victoria = False
            return

        # Verificar si el jugador sale de la zona por primera vez
        if not self.jugador_salio and not self.jugador_en_zona_inicio():
            self.jugador_salio = True
        
        # Los robots patrullan solo si el jugador no ha salido aún
        forzar_patrulla = not self.jugador_salio

        # Actualizar robots
        for robot in self.robots:
            # Pasar las paredes al navegador A* solo una vez
            if not hasattr(robot, 'obstaculos_actualizados') or not robot.obstaculos_actualizados:
                robot.navegador.actualizar_obstaculos(self.laberinto.obtener_paredes_para_astar())
                robot.obstaculos_actualizados = True

            robot.actualizar(
                self.jugador.x, 
                self.jugador.y, 
                self.robots,
                forzar_patrulla=forzar_patrulla
            )
        
        # Verificar colisiones
        self.verificar_colisiones()
        self.verificar_colisiones_robots()

    def dibujar(self):
        self.pantalla.fill(NEGRO)

        if self.jugando:

            # Dibujamos el laberinto
            self.laberinto.dibujar(self.pantalla)

            # Solo dibujar la zona de inicio si el jugador no ha salido
            if not self.jugador_salio:
                pygame.draw.rect(self.pantalla, (50, 50, 50), self.zona_inicio, 2)
            
            self.jugador.dibujar(self.pantalla)
            # Dibujar robots
            for robot in self.robots:
                robot.dibujar(self.pantalla)
        else:
            # Dibuja el laberinto de fondo incluso en la pantalla de Game Over
            self.laberinto.dibujar(self.pantalla)

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

