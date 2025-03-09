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

        # Nivel actual
        self.nivel_actual = 1

        # Definir zona de inicio
        margen = 50
        tamano_zona = 150
        self.zona_inicio = pygame.Rect(
            margen, 
            ALTO_PANTALLA - margen - tamano_zona,
            tamano_zona,
            tamano_zona
        )

        # Definir zona de salida (portal al siguiente nivel)
        self.zona_salida = pygame.Rect(
            ANCHO_PANTALLA - margen - tamano_zona,
            margen,
            tamano_zona,
            tamano_zona
        )

        # Inicializar el laberinto
        self.laberinto = Laberinto(self.nivel_actual)

        # Estado del juego
        self.reiniciar_juego()

    def jugador_en_zona_inicio(self):
        return self.zona_inicio.colliderect(self.jugador.cuadrado)

    def reiniciar_juego(self):
        jugador_x, jugador_y = self.calcular_posicion_segura_jugador()
        # Crear jugador en el centro de la zona de inicio
        self.jugador = Jugador(jugador_x, jugador_y)

        #crear robots
        self.robots = []
        self.crear_robot(3 + self.nivel_actual)

        # Estado de juego
        self.jugando = True
        self.victoria = False
        self.jugador_salio = False  # controlar si el jugador ya salió del cuadro seguro
        self.pasando_nivel = False  # controlar la transición entre niveles

    def calcular_posicion_segura_jugador(self):
        """
        Calcula una posición segura para el jugador según el nivel actual,
        asegurándose de que no esté sobre o demasiado cerca de una pared
        """
        # Posiciones iniciales predefinidas según el nivel
        if self.nivel_actual == 1:
            # Para el primer nivel, usar el centro de la zona de inicio
            jugador_x = self.zona_inicio.centerx
            jugador_y = self.zona_inicio.centery
        elif self.nivel_actual == 2:
            # Para el segundo nivel, ubicar en la esquina inferior izquierda con un margen seguro
            jugador_x = 50
            jugador_y = ALTO_PANTALLA - 100
        elif self.nivel_actual == 3:
            # Para el tercer nivel, ubicar en la esquina inferior izquierda con un margen seguro
            jugador_x = 50
            jugador_y = ALTO_PANTALLA - 100
        else:
            # Posición predeterminada en caso de error
            jugador_x = 50
            jugador_y = ALTO_PANTALLA - 100

        # Verificar que la posición no colisione con paredes
        rect_jugador = pygame.Rect(jugador_x - ANCHO_JUGADOR / 2, jugador_y - ALTO_JUGADOR / 2,
                                   ANCHO_JUGADOR, ALTO_JUGADOR)

        # Si hay colisión, buscar una posición cercana sin colisiones
        if self.laberinto.verificar_colision(rect_jugador):
            # Buscar en un área alrededor de la posición original
            for dx in range(-50, 51, 10):
                for dy in range(-50, 51, 10):
                    nueva_x = jugador_x + dx
                    nueva_y = jugador_y + dy

                    if 20 <= nueva_x <= ANCHO_PANTALLA - 20 and 20 <= nueva_y <= ALTO_PANTALLA - 20:
                        rect_prueba = pygame.Rect(nueva_x - ANCHO_JUGADOR / 2, nueva_y - ALTO_JUGADOR / 2,
                                                  ANCHO_JUGADOR, ALTO_JUGADOR)

                        # Verificar también un margen extra alrededor del jugador
                        rect_seguridad = pygame.Rect(nueva_x - ANCHO_JUGADOR, nueva_y - ALTO_JUGADOR,
                                                     ANCHO_JUGADOR * 2, ALTO_JUGADOR * 2)

                        if not self.laberinto.verificar_colision(
                                rect_prueba) and not self.laberinto.verificar_colision_amplia(rect_seguridad):
                            return nueva_x, nueva_y

            # Si no encontramos una posición segura, usar una posición fija segura según el nivel
            if self.nivel_actual == 2:
                return 150, 550  # Posición alternativa para nivel 2
            elif self.nivel_actual == 3:
                return 120, 520  # Posición alternativa para nivel 3
            else:
                return 100, 500  # Posición alternativa general

        return jugador_x, jugador_y

    def crear_robot(self, cantidad):
        # Posiciones adaptadas según el nivel
        posiciones = []

        # Diferentes patrones de posición según el nivel
        if self.nivel_actual == 1:
            posiciones = [
                (600, 80),  # Arriba derecha
                (700, 80),  # Arriba derecha
                (500, 300),  # Centro derecha
                (600, 300),  # Centro derecha
            ]
        elif self.nivel_actual == 2:
            posiciones = [
                (600, 50),  # Arriba derecha
                (700, 120),  # Arriba derecha
                (500, 250),  # Centro derecha
                (600, 350),  # Centro derecha
                (500, 450),  # Abajo derecha
                (700, 500),  # Abajo derecha
            ]
        elif self.nivel_actual == 3:
            posiciones = [
                (600, 40),  # Arriba derecha
                (700, 120),  # Arriba derecha
                (500, 250),  # Centro derecha
                (600, 350),  # Centro derecha
                (500, 450),  # Abajo derecha
                (700, 500),  # Abajo derecha
                (300, 250),  # Centro
                (400, 450),  # Centro
            ]

        # Limitar la cantidad de robots según las posiciones disponibles
        cantidad = min(cantidad, len(posiciones))

        for i in range(cantidad):
            x, y = posiciones[i]

            # Verificar que la posición no esté sobre una pared
            temp_rect = pygame.Rect(x, y, ANCHO_JUGADOR, ALTO_JUGADOR)
            if self.laberinto.verificar_colision(temp_rect):
                # Buscar una posición cercana que no colisione
                posicion_valida = False
                for dx in range(-50, 51, 10):
                    for dy in range(-50, 51, 10):
                        nueva_x = x + dx
                        nueva_y = y + dy
                        if 0 <= nueva_x < ANCHO_PANTALLA - ANCHO_JUGADOR and 0 <= nueva_y < ALTO_PANTALLA - ALTO_JUGADOR:
                            temp_rect = pygame.Rect(nueva_x, nueva_y, ANCHO_JUGADOR, ALTO_JUGADOR)
                            if not self.laberinto.verificar_colision(temp_rect):
                                x, y = nueva_x, nueva_y
                                posicion_valida = True
                                break
                    if posicion_valida:
                        break

                # Si no se encontró posición válida, saltar este robot
                if not posicion_valida:
                    continue

            # Crear robot en la posición válida
            nuevo_robot = Robot(x, y)
            # Crear puntos de patrulla simples: posición actual y un punto cercano en una dirección aleatoria
            direccion = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            dx, dy = direccion

            # Punto alternativo a corta distancia
            alt_x = x + dx * 40
            alt_y = y + dy * 40

            # Verificar que el punto alternativo no colisione con paredes
            alt_rect = pygame.Rect(alt_x, alt_y, ANCHO_JUGADOR, ALTO_JUGADOR)
            if not self.laberinto.verificar_colision(alt_rect):
                nuevo_robot.puntos_patrulla = [(x, y), (alt_x, alt_y)]
            else:
                # Si colisiona, usar solo la posición actual duplicada (permanecerá casi inmóvil)
                nuevo_robot.puntos_patrulla = [(x, y), (x + 5, y + 5)]

            nuevo_robot.punto_patrulla_actual = 0
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

        # Verificar si el jugador llega a la zona de salida
        if self.zona_salida.colliderect(self.jugador.cuadrado) and len(self.robots) == 0:
            if self.nivel_actual < 3:
                # Pasar al siguiente nivel
                self.pasando_nivel = True
                self.nivel_actual += 1

                # Primero cambiar el laberinto para el nuevo nivel
                self.laberinto.cambiar_nivel(self.nivel_actual)

                # Luego reiniciar el juego para el nuevo nivel
                self.reiniciar_juego()

                # Pausar brevemente para asegurar que todo se inicialice correctamente
                pygame.time.delay(100)
                return
            else:
                # Victoria final
                self.jugando = False
                self.victoria = True
                return

        # Verificar victoria por eliminar a todos los robots
        if len(self.robots) == 0 and not self.pasando_nivel:
            # No finaliza el juego, solo muestra que hay que llegar a la salida
            pass
    
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

        self.jugador.actualizar(self.laberinto)

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
                forzar_patrulla=forzar_patrulla,
                laberinto=self.laberinto  # Pasar el laberinto para verificar colisiones
            )
        
        # Verificar colisiones
        self.verificar_colisiones()
        self.verificar_colisiones_robots()

    def dibujar(self):
        self.pantalla.fill(NEGRO)

        if self.jugando:

            # Dibujamos el laberinto
            self.laberinto.dibujar(self.pantalla)

            # Dibujamos la zona de salida (verde claro)
            if len(self.robots) == 0:
                pygame.draw.rect(self.pantalla, (100, 255, 100), self.zona_salida)

            # Solo dibujar la zona de inicio si el jugador no ha salido
            if not self.jugador_salio:
                pygame.draw.rect(self.pantalla, (50, 50, 50), self.zona_inicio, 2)
            self.jugador.dibujar(self.pantalla)

            # Dibujar robots
            for robot in self.robots:
                robot.dibujar(self.pantalla)

            # Mostrar nivel actual
            fuente = pygame.font.Font(None, 36)
            texto_nivel = f"Nivel: {self.nivel_actual}"
            superficie_nivel = fuente.render(texto_nivel, True, BLANCO)
            self.pantalla.blit(superficie_nivel, (10, 10))

            # Mostrar indicaciones si todos los robots están eliminados
            if len(self.robots) == 0:
                fuente_indicacion = pygame.font.Font(None, 24)
                texto_indicacion = "¡Dirígete a la salida (cuadro verde)!"
                superficie_indicacion = fuente_indicacion.render(texto_indicacion, True, BLANCO)
                rect_indicacion = superficie_indicacion.get_rect(center=(ANCHO_PANTALLA // 2, 30))
                self.pantalla.blit(superficie_indicacion, rect_indicacion)

        else:
            fuente = pygame.font.Font(None, 74)
            if self.victoria:
                if self.nivel_actual == 3:
                    texto = "¡VICTORIA FINAL!"
                else:
                    texto = f"¡NIVEL {self.nivel_actual} COMPLETADO!"
            else:
                texto = "¡GAME OVER!"
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

