import pygame
import random
import math
import os
from src.constantes import *
from src.entidades.jugador import Jugador
from src.entidades.robot import Robot
from src.utilidades.colisiones import detectar_colision_entidades, detectar_colision_balas_entidad
from src.laberinto import Laberinto

class Menu:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.estado_menu = "principal"  # principal, instrucciones, pausa, game_over, victoria
        # Cargar fuentes
        self.fuente_titulo = pygame.font.Font(None, 74)
        self.fuente_opciones = pygame.font.Font(None, 48)
        self.fuente_pequena = pygame.font.Font(None, 36)
        # Colores adicionales para el menú
        self.color_seleccion = (255, 255, 0)  # Amarillo para opción seleccionada
        self.opcion_seleccionada = 0
        # Opciones del menú principal
        self.opciones_principal = ["Jugar", "Instrucciones", "Salir"]
        # Opciones del menú de pausa
        self.opciones_pausa = ["Continuar", "Reiniciar", "Salir al menú"]
        # Opciones de game over
        self.opciones_game_over = ["Reiniciar", "Salir al menú"]
        # Tiempo para animaciones
        self.tiempo = 0

    def actualizar(self):
        self.tiempo += 1

    def manejar_eventos(self, evento):
        if evento.type == pygame.KEYDOWN:
            if self.estado_menu in ["principal", "pausa", "game_over", "victoria"]:
                if evento.key == pygame.K_UP:
                    self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.obtener_opciones_actuales())
                elif evento.key == pygame.K_DOWN:
                    self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.obtener_opciones_actuales())
                elif evento.key == pygame.K_RETURN:
                    return self.seleccionar_opcion()
            if evento.key == pygame.K_ESCAPE and self.estado_menu == "instrucciones":
                self.estado_menu = "principal"
                self.opcion_seleccionada = 0
                return None
        return None

    def obtener_opciones_actuales(self):
        if self.estado_menu == "principal":
            return self.opciones_principal
        elif self.estado_menu == "pausa":
            return self.opciones_pausa
        elif self.estado_menu == "game_over" or self.estado_menu == "victoria":
            return self.opciones_game_over
        elif self.estado_menu == "instrucciones":
            return ["Volver"]
        return ["Volver"]

    def seleccionar_opcion(self):
        if self.estado_menu == "principal":
            if self.opcion_seleccionada == 0:  # Jugar
                return "jugar"
            elif self.opcion_seleccionada == 1:  # Instrucciones
                self.estado_menu = "instrucciones"
                return None
            elif self.opcion_seleccionada == 2:  # Salir
                return "salir"
        elif self.estado_menu == "pausa":
            if self.opcion_seleccionada == 0:  # Continuar
                return "continuar"
            elif self.opcion_seleccionada == 1:  # Reiniciar
                return "reiniciar"
            elif self.opcion_seleccionada == 2:  # Salir al menú
                return "menu"
        elif self.estado_menu == "game_over" or self.estado_menu == "victoria":
            if self.opcion_seleccionada == 0:  # Reiniciar
                return "reiniciar"
            elif self.opcion_seleccionada == 1:  # Salir al menú
                return "menu"
        return None

    def dibujar(self):
        # Fondo con efecto de desvanecimiento
        s = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))  # Fondo semi-transparente
        self.pantalla.blit(s, (0, 0))

        if self.estado_menu == "principal":
            self.dibujar_menu_principal()
        elif self.estado_menu == "instrucciones":
            self.dibujar_instrucciones()
        elif self.estado_menu == "pausa":
            self.dibujar_menu_pausa()
        elif self.estado_menu == "game_over":
            self.dibujar_game_over()
        elif self.estado_menu == "victoria":
            self.dibujar_victoria()

    def dibujar_menu_principal(self):
        # Título con efecto de pulso
        escala = 1.0 + 0.05 * math.sin(self.tiempo * 0.05)
        titulo = self.fuente_titulo.render("BERSERK (1980)", True, ROJO)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 100))
        # Aplicar escala
        ancho_original = titulo.get_width()
        alto_original = titulo.get_height()
        titulo_escalado = pygame.transform.scale(titulo,
                                                 (int(ancho_original * escala),
                                                  int(alto_original * escala)))
        rect_titulo_escalado = titulo_escalado.get_rect(center=(ANCHO_PANTALLA // 2, 100))
        self.pantalla.blit(titulo_escalado, rect_titulo_escalado)

        # Opciones
        for i, opcion in enumerate(self.opciones_principal):
            color = self.color_seleccion if i == self.opcion_seleccionada else BLANCO
            y_pos = 250 + i * 60
            # Efecto de flecha para la opción seleccionada
            if i == self.opcion_seleccionada:
                flecha = "> " + opcion + " <"
                texto = self.fuente_opciones.render(flecha, True, color)
            else:
                texto = self.fuente_opciones.render(opcion, True, color)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, y_pos))
            self.pantalla.blit(texto, rect_texto)

        # Créditos
        creditos = self.fuente_pequena.render("Proyecto de IA - 2025", True, BLANCO)
        rect_creditos = creditos.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 50))
        self.pantalla.blit(creditos, rect_creditos)

    def dibujar_instrucciones(self):
        # Título
        titulo = self.fuente_titulo.render("INSTRUCCIONES", True, BLANCO)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 80))
        self.pantalla.blit(titulo, rect_titulo)

        # Instrucciones
        instrucciones = [
            "Objetivo: Escapa de la base llena de robots",
            "Controles:",
            "- Flechas: Moverse",
            "- W/A/S/D: Disparar",
            "- ESC: Pausar el juego",
            "",
            "Elimina a todos los robots y encuentra la salida",
            "para avanzar al siguiente nivel",
            "",
            "¡Cuidado con las paredes electrificadas!",
            "",
            "Presiona ESC para volver"
        ]

        for i, linea in enumerate(instrucciones):
            texto = self.fuente_pequena.render(linea, True, BLANCO)
            rect_texto = texto.get_rect(midleft=(ANCHO_PANTALLA // 4, 150 + i * 35))
            self.pantalla.blit(texto, rect_texto)

    def dibujar_menu_pausa(self):
        # Título
        titulo = self.fuente_titulo.render("PAUSA", True, BLANCO)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 120))
        self.pantalla.blit(titulo, rect_titulo)

        # Opciones
        for i, opcion in enumerate(self.opciones_pausa):
            color = self.color_seleccion if i == self.opcion_seleccionada else BLANCO
            y_pos = 250 + i * 60
            if i == self.opcion_seleccionada:
                flecha = "> " + opcion + " <"
                texto = self.fuente_opciones.render(flecha, True, color)
            else:
                texto = self.fuente_opciones.render(opcion, True, color)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, y_pos))
            self.pantalla.blit(texto, rect_texto)

    def dibujar_game_over(self):
        # Título con efecto de temblor
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        titulo = self.fuente_titulo.render("GAME OVER", True, ROJO)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2 + offset_x, 120 + offset_y))
        self.pantalla.blit(titulo, rect_titulo)

        # Opciones
        for i, opcion in enumerate(self.opciones_game_over):
            color = self.color_seleccion if i == self.opcion_seleccionada else BLANCO
            y_pos = 250 + i * 60
            if i == self.opcion_seleccionada:
                flecha = "> " + opcion + " <"
                texto = self.fuente_opciones.render(flecha, True, color)
            else:
                texto = self.fuente_opciones.render(opcion, True, color)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, y_pos))
            self.pantalla.blit(texto, rect_texto)

    def dibujar_victoria(self):
        # Título con efecto brillante
        brillo = abs(math.sin(self.tiempo * 0.1)) * 255
        color_brillante = (255, 255, min(100 + int(brillo), 255))
        titulo = self.fuente_titulo.render("¡VICTORIA!", True, color_brillante)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 120))
        self.pantalla.blit(titulo, rect_titulo)

        # Mensaje de felicitación
        mensaje = self.fuente_pequena.render("¡Has escapado de la base robótica!", True, BLANCO)
        rect_mensaje = mensaje.get_rect(center=(ANCHO_PANTALLA // 2, 180))
        self.pantalla.blit(mensaje, rect_mensaje)

        # Opciones
        for i, opcion in enumerate(self.opciones_game_over):
            color = self.color_seleccion if i == self.opcion_seleccionada else BLANCO
            y_pos = 250 + i * 60
            if i == self.opcion_seleccionada:
                flecha = "> " + opcion + " <"
                texto = self.fuente_opciones.render(flecha, True, color)
            else:
                texto = self.fuente_opciones.render(opcion, True, color)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, y_pos))
            self.pantalla.blit(texto, rect_texto)

    def manejar_joystick(self, eje_y, tiempo_actual, ultimo_tiempo):
        """Maneja la navegación del menú con joystick"""
        if tiempo_actual - ultimo_tiempo > 200:  # 200ms para evitar navegación demasiado rápida
            if eje_y > 0.5:  # Hacia abajo
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.obtener_opciones_actuales())
                return tiempo_actual
            elif eje_y < -0.5:  # Hacia arriba
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.obtener_opciones_actuales())
                return tiempo_actual
        return ultimo_tiempo


class Juego:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Berzerk")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True

        # Inicialización de joysticks
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            print(f"Joystick {i} conectado: {joystick.get_name()}")

        # Variables para el control del joystick
        self.joystick_x = 0
        self.joystick_y = 0
        self.ultimo_tiempo_joystick = 0  # Para controlar la sensibilidad en menús

        # Nivel actual
        self.nivel_actual = 1

        # Definir zona de inicio
        margen = 50
        tamano_zona = 80
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

        # Cargar sonidos
        self.cargar_sonidos()

        # Cargar imágenes
        self.cargar_imagenes()

        # Crear menú
        self.menu = Menu(self.pantalla)
        self.estado_juego = "menu"  # menu, jugando, pausa

        # Estado del juego
        self.reiniciar_juego()

        # Sistema de vidas
        self.vidas = 3
        self.tiempo_invulnerabilidad = 0
        self.invulnerable = False

    def cargar_imagenes(self):
        self.imagenes = {}
        try:
            # Crear directorio de imágenes si no existe
            os.makedirs('assets/imagenes', exist_ok=True)

            # Crear imagen para la vida (corazón simple)
            tamano_vida = 25
            superficie_vida = pygame.Surface((tamano_vida, tamano_vida), pygame.SRCALPHA)
            pygame.draw.polygon(superficie_vida, ROJO, [
                (tamano_vida // 2, tamano_vida // 5),
                (tamano_vida - tamano_vida // 5, tamano_vida // 2),
                (tamano_vida // 2, tamano_vida - tamano_vida // 5),
                (tamano_vida // 5, tamano_vida // 2)
            ])
            self.imagenes['vida'] = superficie_vida
        except Exception as e:
            print(f"Error al cargar imágenes: {e}")

    def cargar_sonidos(self):
        self.sonidos = {}
        try:
            # Asegurarse de que existe el directorio
            os.makedirs('assets/sonidos', exist_ok=True)

            # Intentar cargar sonidos si existen
            archivos_sonido = {
                'disparo_jugador': 'assets/sonidos/disparo_jugador.wav',
                'disparo_robot': 'assets/sonidos/disparo_robot.wav',
                'explosion': 'assets/sonidos/explosion.wav',
                'nivel_completado': 'assets/sonidos/nivel_completado.wav',
                'game_over': 'assets/sonidos/game_over.wav',
                'daño': 'assets/sonidos/dano.wav'
            }

            # Música de fondo
            archivo_musica = 'assets/sonidos/musica_fondo.mp3'

            # Cargar sonidos disponibles
            for nombre, ruta in archivos_sonido.items():
                if os.path.exists(ruta):
                    self.sonidos[nombre] = pygame.mixer.Sound(ruta)
                    self.sonidos[nombre].set_volume(0.3)

            # Cargar música si existe
            if os.path.exists(archivo_musica):
                pygame.mixer.music.load(archivo_musica)
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)  # -1 para repetir infinitamente

        except Exception as e:
            print(f"Error al cargar sonidos: {e}")

    def reproducir_sonido(self, nombre_sonido):
        if nombre_sonido in self.sonidos:
            self.sonidos[nombre_sonido].play()

    def jugador_en_zona_inicio(self):
        return self.zona_inicio.colliderect(self.jugador.cuadrado)

    def reiniciar_juego(self):
        jugador_x, jugador_y = self.calcular_posicion_segura_jugador()
        # Crear jugador en el centro de la zona de inicio
        self.jugador = Jugador(jugador_x, jugador_y)

        # Reiniciar los valores del joystick
        self.joystick_x = 0
        self.joystick_y = 0

        # Ajustar velocidad del jugador
        self.jugador.velocidad = VELOCIDAD_JUGADOR

        #crear robots
        self.robots = []
        robots_por_nivel = {
            1: 5,  # Nivel 1: 5 robots
            2: 8,  # Nivel 2: 8 robots
            3: 12  # Nivel 3: 12 robots
        }
        self.crear_robots(robots_por_nivel.get(self.nivel_actual, 5))

        # Estado de juego
        self.jugando = True
        self.victoria = False
        self.jugador_salio = False  # controlar si el jugador ya salió del cuadro seguro
        self.pasando_nivel = False  # controlar la transición entre niveles

        # Resetear estado de invulnerabilidad
        self.invulnerable = False
        self.tiempo_invulnerabilidad = 0


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

    def crear_robots(self, cantidad):
        # Definir la cantidad de robots por nivel
        robots_por_nivel = {
            1: 6,
            2: 8,
            3: 10
        }
        cantidad_objetivo = robots_por_nivel.get(self.nivel_actual, 6)

        # Posiciones específicas y rutas de patrulla para cada nivel
        robots_predefinidos = {
            1: [
                # [posición_x, posición_y, [punto_patrulla_1_x, punto_patrulla_1_y, punto_patrulla_2_x, punto_patrulla_2_y]]
                [600, 80, 650, 80, 700, 80],  # Robot 1: superior derecha
                [600, 150, 600, 200, 650, 150],  # Robot 2: medio derecha superior
                [600, 300, 650, 300, 700, 300],  # Robot 3: medio derecha
                [600, 500, 700, 500, 650, 450],  # Robot 4: inferior derecha
                [200, 100, 250, 100, 200, 150],  # Robot 5: superior izquierda
                [200, 300, 150, 300, 250, 300],  # Robot 6: medio izquierda
                # Posiciones extra por si algunas no son válidas
                [400, 100, 450, 100, 400, 150],  # Extra 1
                [400, 300, 450, 300, 400, 350],  # Extra 2
                [400, 500, 450, 500, 400, 450]  # Extra 3
            ],
            2: [
                [600, 80, 700, 80, 650, 120],  # Robot 1: superior derecha
                [600, 180, 650, 180, 700, 180],  # Robot 2: superior media derecha
                [600, 250, 650, 250, 700, 100],  # Robot 3: medio derecha
                [600, 380, 650, 380, 700, 380],  # Robot 4: medio inferior derecha
                [600, 520, 650, 520, 700, 520],  # Robot 5: inferior derecha
                [150, 80, 200, 80, 150, 120],  # Robot 6: superior izquierda
                [150, 380, 200, 280, 150, 320],  # Robot 7: medio izquierda
                [350, 480, 400, 480, 350, 520]  # Robot 8: centro-inferior
            ],
            3: [
                [150, 50, 200, 50, 150, 100],  # Robot 1: superior izquierda
                [400, 50, 450, 50, 500, 50],  # Robot 2: superior central
                [650, 50, 700, 50, 650, 100],  # Robot 3: superior derecha
                [750, 150, 700, 150, 750, 200],  # Robot 4: derecha superior
                [100, 350, 150, 350, 100, 400],  # Robot 5: izquierda media
                [550, 230, 600, 230, 650, 230],  # Robot 6
                [650, 530, 700, 530, 680, 580],  # Robot 7
                [150, 600, 200, 600, 150, 650],  # Robot 8: izquierda inferior
                [500, 600, 550, 600, 500, 650],  # Robot 9: área inferior
                [350, 600, 400, 600, 380, 650],  # Robot 10: área inferior izquierda
                # Posiciones extra
                [300, 50, 350, 50, 300, 100],  # Extra 1
                [450, 350, 500, 350, 450, 400],  # Extra 2
                [250, 500, 300, 500, 250, 550],  # Extra 3
                [400, 200, 450, 200, 400, 250]  # Extra 4
            ]
        }

        # Velocidad base de los robots, aumenta con el nivel
        velocidad_base = VELOCIDAD_ROBOT
        velocidad_por_nivel = {
            1: velocidad_base,
            2: velocidad_base * 1.3,  # 30% más rápido en nivel 2
            3: velocidad_base * 1.6  # 60% más rápido en nivel 3
        }
        velocidad_robot = velocidad_por_nivel.get(self.nivel_actual, velocidad_base)

        # Limpiar la lista de robots
        self.robots = []

        # Obtener las posiciones predefinidas para este nivel
        robots_nivel = robots_predefinidos.get(self.nivel_actual, [])

        # Si no hay definiciones para este nivel, usar un conjunto predeterminado
        if not robots_nivel:
            robots_nivel = robots_predefinidos.get(1, [])

        # Contador de robots creados
        robots_creados = 0

        # Intentar crear robots con todas las definiciones disponibles
        for pos_robot in robots_nivel:
            # Si ya tenemos suficientes robots, salir
            if robots_creados >= cantidad_objetivo:
                break

            x, y = pos_robot[0], pos_robot[1]  # Posición del robot

            # Verificar que la posición no esté sobre una pared
            temp_rect = pygame.Rect(x - ANCHO_JUGADOR / 2, y - ALTO_JUGADOR / 2,
                                    ANCHO_JUGADOR, ALTO_JUGADOR)

            if self.laberinto.verificar_colision(temp_rect):
                continue  # Saltar este robot si está sobre una pared

            # Crear robot en la posición
            nuevo_robot = Robot(x, y)

            # Ajustar velocidad del robot según el nivel
            nuevo_robot.velocidad = velocidad_robot

            # Asignar puntos de patrulla específicos
            puntos_patrulla = []
            if len(pos_robot) >= 6:  # Si hay puntos de patrulla definidos
                # Posición inicial
                puntos_patrulla.append((x, y))

                # Punto de patrulla 1
                px1, py1 = pos_robot[2], pos_robot[3]
                puntos_patrulla.append((px1, py1))

                # Punto de patrulla 2
                px2, py2 = pos_robot[4], pos_robot[5]
                puntos_patrulla.append((px2, py2))
            else:
                # Si no hay puntos definidos, usar la posición actual
                puntos_patrulla = [(x, y), (x + 20, y), (x, y + 20)]

            # Verificar que los puntos de patrulla sean accesibles
            puntos_validos = []
            for px, py in puntos_patrulla:
                temp_rect = pygame.Rect(px - ANCHO_JUGADOR / 2, py - ALTO_JUGADOR / 2,
                                        ANCHO_JUGADOR, ALTO_JUGADOR)
                if not self.laberinto.verificar_colision(temp_rect):
                    # Verificar camino libre si no es el primer punto
                    if len(puntos_validos) == 0 or self.verificar_camino_libre(puntos_validos[-1][0],
                                                                               puntos_validos[-1][1], px, py):
                        puntos_validos.append((px, py))

            # Si no hay suficientes puntos válidos, añadir la posición actual
            if len(puntos_validos) < 2:
                puntos_validos = [(x, y), (x + 10, y)]

            nuevo_robot.puntos_patrulla = puntos_validos
            nuevo_robot.punto_patrulla_actual = 0

            # Añadir el robot a la lista
            self.robots.append(nuevo_robot)
            robots_creados += 1

        # Si no tenemos suficientes robots, crear más en posiciones seguras
        if robots_creados < cantidad_objetivo:
            # Definir zonas seguras para robots adicionales
            zonas_seguras = {
                1: [
                    (300, 100, 350, 150),
                    (300, 300, 350, 350),
                    (300, 500, 350, 550)
                ],
                2: [
                    (300, 100, 350, 150),
                    (300, 300, 350, 350),
                    (300, 500, 350, 550)
                ],
                3: [
                    (300, 100, 350, 150),
                    (300, 300, 350, 350),
                    (300, 500, 350, 550),
                    (550, 250, 600, 300),
                    (450, 400, 500, 450)
                ]
            }

            zonas = zonas_seguras.get(self.nivel_actual, [])

            # Crear robots adicionales
            for i in range(cantidad_objetivo - robots_creados):
                if not zonas:
                    break

                zona = zonas[i % len(zonas)]
                x = (zona[0] + zona[2]) // 2
                y = (zona[1] + zona[3]) // 2

                nuevo_robot = Robot(x, y)
                nuevo_robot.velocidad = velocidad_robot

                # Puntos de patrulla simples
                puntos = [(x, y), (x + 30, y), (x, y + 30)]
                nuevo_robot.puntos_patrulla = puntos
                nuevo_robot.punto_patrulla_actual = 0

                self.robots.append(nuevo_robot)
                robots_creados += 1

        print(f"Creados {len(self.robots)} robots en el nivel {self.nivel_actual}")

    def crear_puntos_patrulla_en_zona(self, robot, zona):
        """Crea puntos de patrulla para el robot dentro de una zona específica"""
        x_min, y_min, x_max, y_max = zona

        # Posición actual del robot
        puntos = [(robot.x, robot.y)]

        # Intentar añadir solo 1 punto adicional pero bien verificado
        intentos = 0
        max_intentos = 20

        while len(puntos) < 2 and intentos < max_intentos:
            intentos += 1

            # Generar punto aleatorio dentro de la zona
            x = random.randint(x_min + 15, x_max - 15)  # Margen para evitar paredes
            y = random.randint(y_min + 15, y_max - 15)  # Margen para evitar paredes

            # Verificar que no esté sobre una pared
            temp_rect = pygame.Rect(x - ANCHO_JUGADOR / 2, y - ALTO_JUGADOR / 2,
                                    ANCHO_JUGADOR, ALTO_JUGADOR)

            if not self.laberinto.verificar_colision(temp_rect):
                # Verificar con más precisión que hay un camino libre
                if self.verificar_camino_libre(robot.x, robot.y, x, y):
                    puntos.append((x, y))

        # Si no pudimos añadir un punto, usar uno muy cercano al robot
        if len(puntos) < 2:
            # Buscar en círculos concéntricos muy pequeños
            for distancia in [10, 15, 20]:
                encontrado = False
                for angulo in range(0, 360, 45):
                    rad = math.radians(angulo)
                    nx = robot.x + math.cos(rad) * distancia
                    ny = robot.y + math.sin(rad) * distancia

                    temp_rect = pygame.Rect(nx - ANCHO_JUGADOR / 2, ny - ALTO_JUGADOR / 2,
                                            ANCHO_JUGADOR, ALTO_JUGADOR)

                    if not self.laberinto.verificar_colision(temp_rect):
                        puntos.append((nx, ny))
                        encontrado = True
                        break

                if encontrado:
                    break

            # Si aún no hay puntos, usar una variación mínima
            if len(puntos) < 2:
                puntos.append((robot.x + 5, robot.y + 5))

        robot.puntos_patrulla = puntos
        robot.punto_patrulla_actual = 0

    def verificar_camino_libre(self, x1, y1, x2, y2):
        """Verifica si hay un camino libre entre dos puntos"""
        # Calcular la distancia entre los puntos
        distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Más puntos para distancias mayores
        num_pasos = max(10, int(distancia / 10))

        # Verificar varios puntos a lo largo de la ruta
        for i in range(num_pasos + 1):
            t = i / num_pasos
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t

            # Crear un cuadrado ligeramente más grande para verificar colisiones
            # (margen de seguridad para evitar que el robot se acerque demasiado a las paredes)
            margen = 5  # Margen de seguridad
            ancho_check = ANCHO_JUGADOR + margen * 2
            alto_check = ALTO_JUGADOR + margen * 2

            rect_check = pygame.Rect(x - ancho_check / 2, y - alto_check / 2, ancho_check, alto_check)

            if self.laberinto.verificar_colision(rect_check):
                return False  # Hay un obstáculo en el camino

        return True  # No hay obstáculos en el camino

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
                self.reproducir_sonido('explosion')
                self.robots.remove(robot)  # Eliminar robot si es golpeado

        # Verificar colisiones entre balas de robots y jugador
        if not self.invulnerable:
            for robot in self.robots:
                if detectar_colision_balas_entidad(robot.balas, self.jugador):
                    self.perder_vida()
                    return

        # Verificar colisiones directas entre jugador y robots
        if not self.invulnerable:
            for robot in self.robots:
                if detectar_colision_entidades(self.jugador, robot):
                    self.perder_vida()
                    return

        # Verificar colisiones entre jugador y paredes
        if self.laberinto.verificar_colision(self.jugador.cuadrado):
            self.perder_vida()
            return

        # Verificar si el jugador llega a la zona de salida
        if self.zona_salida.colliderect(self.jugador.cuadrado) and len(self.robots) == 0:
            self.reproducir_sonido('nivel_completado')
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
                self.menu.estado_menu = "victoria"
                self.estado_juego = "menu"
                return

        # Verificar victoria por eliminar a todos los robots
        if len(self.robots) == 0 and not self.pasando_nivel:
            # No finaliza el juego, solo muestra que hay que llegar a la salida
            pass

    def perder_vida(self):
        """Gestiona la pérdida de una vida del jugador"""
        if not self.invulnerable:
            self.reproducir_sonido('daño')
            self.vidas -= 1

            if self.vidas <= 0:
                # Game over
                self.reproducir_sonido('game_over')
                self.jugando = False
                self.victoria = False
                self.menu.estado_menu = "game_over"
                self.estado_juego = "menu"
            else:
                # Periodo de invulnerabilidad
                self.invulnerable = True
                self.tiempo_invulnerabilidad = 120  # 2 segundos a 60 FPS

                # Reposicionar al jugador en un lugar seguro
                x, y = self.calcular_posicion_segura_jugador()
                self.jugador.x = x
                self.jugador.y = y
                self.jugador.cuadrado.x = x
                self.jugador.cuadrado.y = y

    def manejar_eventos(self):

        tiempo_actual = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False

            # Eventos de joystick
            elif evento.type == pygame.JOYAXISMOTION:
                # Movimiento en los menús con el joystick izquierdo
                if self.estado_juego == "menu" or self.estado_juego == "pausa":
                    if evento.axis == 1:  # Eje Y del joystick izquierdo
                        # Control de velocidad para el menú
                        if tiempo_actual - self.ultimo_tiempo_joystick > 200:  # 200ms entre movimientos
                            # Verificar que hay opciones para evitar división por cero
                            opciones = self.menu.obtener_opciones_actuales()
                            if opciones and len(opciones) > 0:
                                if evento.value > 0.5:  # Hacia abajo
                                    self.menu.opcion_seleccionada = (self.menu.opcion_seleccionada + 1) % len(opciones)
                                    self.ultimo_tiempo_joystick = tiempo_actual
                                elif evento.value < -0.5:  # Hacia arriba
                                    self.menu.opcion_seleccionada = (self.menu.opcion_seleccionada - 1) % len(opciones)
                                    self.ultimo_tiempo_joystick = tiempo_actual

                # Movimiento del jugador con joystick izquierdo en modo juego
                elif self.estado_juego == "jugando":
                    if evento.axis < 2:  # Los primeros dos ejes (X, Y) del joystick izquierdo
                        if evento.axis == 0:
                            self.joystick_x = evento.value
                        elif evento.axis == 1:
                            self.joystick_y = evento.value

            elif evento.type == pygame.JOYBUTTONDOWN:
                # Botones de dirección para disparar
                # Mapeo de botones según su posición
                if self.estado_juego == "jugando":
                    if evento.button == 0:  # Botón 1 - dispara hacia arriba
                        self.jugador.disparar(0, -1)
                        self.reproducir_sonido('disparo_jugador')
                    elif evento.button == 1:  # Botón 2 - dispara hacia la derecha
                        self.jugador.disparar(1, 0)
                        self.reproducir_sonido('disparo_jugador')
                    elif evento.button == 2:  # Botón 3 - dispara hacia abajo
                        self.jugador.disparar(0, 1)
                        self.reproducir_sonido('disparo_jugador')
                    elif evento.button == 3:  # Botón 4 - dispara hacia la izquierda
                        self.jugador.disparar(-1, 0)
                        self.reproducir_sonido('disparo_jugador')
                    elif evento.button == 7 or evento.button == 9:  # Botón Start - pausa el juego
                        self.estado_juego = "pausa"
                        self.menu.estado_menu = "pausa"
                        self.menu.opcion_seleccionada = 0

                # Navegación en menús
                if self.estado_juego == "menu" or self.estado_juego == "pausa":
                    if evento.button == 0:  # Botón 1 - Seleccionar opción
                        opciones = self.menu.obtener_opciones_actuales()
                        if opciones and len(opciones) > 0:
                            accion = self.menu.seleccionar_opcion()
                            if accion == "jugar":
                                self.estado_juego = "jugando"
                                self.nivel_actual = 1
                                self.vidas = 3
                                self.laberinto.cambiar_nivel(self.nivel_actual)
                                self.reiniciar_juego()
                            elif accion == "salir":
                                self.ejecutando = False
                            elif accion == "reiniciar":
                                self.estado_juego = "jugando"
                                self.nivel_actual = 1
                                self.vidas = 3
                                self.laberinto.cambiar_nivel(self.nivel_actual)
                                self.reiniciar_juego()
                            elif accion == "continuar":
                                self.estado_juego = "jugando"
                            elif accion == "menu":
                                self.menu.estado_menu = "principal"
                                self.menu.opcion_seleccionada = 0
                                self.estado_juego = "menu"

                    # Botón para volver
                    elif evento.button == 1 or evento.button == 6:  # Botón 2 o Select para volver
                        if self.estado_juego == "pausa":
                            self.estado_juego = "jugando"
                        elif self.menu.estado_menu == "instrucciones":
                            self.menu.estado_menu = "principal"
                            self.menu.opcion_seleccionada = 0

            # Eventos con el teclado
            if self.estado_juego == "menu":
                accion = self.menu.manejar_eventos(evento)
                if accion == "jugar":
                    self.estado_juego = "jugando"
                    self.nivel_actual = 1
                    self.vidas = 3
                    self.laberinto.cambiar_nivel(self.nivel_actual)
                    self.reiniciar_juego()
                elif accion == "salir":
                    self.ejecutando = False
                elif accion == "reiniciar":
                    self.estado_juego = "jugando"
                    self.nivel_actual = 1
                    self.vidas = 3
                    self.laberinto.cambiar_nivel(self.nivel_actual)
                    self.reiniciar_juego()
                elif accion == "menu":
                    self.menu.estado_menu = "principal"
                    self.menu.opcion_seleccionada = 0

            elif self.estado_juego == "jugando":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.estado_juego = "pausa"
                        self.menu.estado_menu = "pausa"
                        self.menu.opcion_seleccionada = 0

            elif self.estado_juego == "pausa":
                accion = self.menu.manejar_eventos(evento)
                if accion == "continuar":
                    self.estado_juego = "jugando"
                elif accion == "reiniciar":
                    self.estado_juego = "jugando"
                    self.vidas = 3
                    self.reiniciar_juego()
                elif accion == "menu":
                    self.menu.estado_menu = "principal"
                    self.menu.opcion_seleccionada = 0
                    self.estado_juego = "menu"

        if self.estado_juego == "jugando":
            # Teclas presionadas
            teclas = pygame.key.get_pressed()
            dx = teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]
            dy = teclas[pygame.K_DOWN] - teclas[pygame.K_UP]

            # Combinar con movimiento del joystick si existe
            if hasattr(self, 'joystick_x') and hasattr(self, 'joystick_y'):
                umbral = 0.2
                joystick_dx = self.joystick_x if abs(self.joystick_x) > umbral else 0
                joystick_dy = self.joystick_y if abs(self.joystick_y) > umbral else 0

                # Si hay input del joystick, usarlo en lugar del teclado
                if joystick_dx != 0 or joystick_dy != 0:
                    dx = joystick_dx
                    dy = joystick_dy

            self.jugador.mover(dx, dy)

            #Sistema de disparo
            if teclas[pygame.K_w]: #Arriba
                self.jugador.disparar(0, -1)
                self.reproducir_sonido('disparo_jugador')
            if teclas[pygame.K_s]: #Abajo
                self.jugador.disparar(0, 1)
                self.reproducir_sonido('disparo_jugador')
            if teclas[pygame.K_a]: #Izquierda
                self.jugador.disparar(-1, 0)
                self.reproducir_sonido('disparo_jugador')
            if teclas[pygame.K_d]:  #Derecha
                self.jugador.disparar(1, 0)
                self.reproducir_sonido('disparo_jugador')

    def actualizar(self):

        if self.estado_juego == "menu":
            self.menu.actualizar()
            return

        if self.estado_juego == "pausa":
            return

        if not self.jugando:
            return

        self.jugador.actualizar(self.laberinto)

        # Actualizar estado de invulnerabilidad
        if self.invulnerable:
            self.tiempo_invulnerabilidad -= 1
            if self.tiempo_invulnerabilidad <= 0:
                self.invulnerable = False

        # Verificar colisiones del jugador con las paredes después de actualizar
        if self.laberinto.verificar_colision(self.jugador.cuadrado):
            # Si hay colisión, pierde una vida
            self.perder_vida()
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

            # Hacer que los robots disparen ocasionalmente
            if robot.estado_actual == "persecución" and random.random() < 0.01:
                dx = self.jugador.x - robot.x
                dy = self.jugador.y - robot.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    dx /= dist
                    dy /= dist
                    robot.disparar_a_jugador(self.jugador.x, self.jugador.y)
                    self.reproducir_sonido('disparo_robot')
        
        # Verificar colisiones
        self.verificar_colisiones()
        self.verificar_colisiones_robots()

    def dibujar(self):
        self.pantalla.fill(NEGRO)

        # Dibuja el laberinto como fondo
        self.laberinto.dibujar(self.pantalla)

        if self.estado_juego == "jugando" or self.estado_juego == "pausa":

            # Dibuja la zona de salida (verde claro)
            if len(self.robots) == 0:
                pygame.draw.rect(self.pantalla, (100, 255, 100), self.zona_salida)

            # Solo dibujar la zona de inicio si el jugador no ha salido
            if not self.jugador_salio:
                pygame.draw.rect(self.pantalla, (50, 50, 50), self.zona_inicio, 2)

            # Dibujar jugador con efecto de parpadeo si es invulnerable
            if self.invulnerable:
                if self.tiempo_invulnerabilidad % 10 < 5:  # Parpadeo
                    self.jugador.dibujar(self.pantalla)
            else:
                self.jugador.dibujar(self.pantalla)

            # Dibujar robots
            for robot in self.robots:
                robot.dibujar(self.pantalla)

            # Mostrar nivel actual
            fuente = pygame.font.Font(None, 36)
            texto_nivel = f"Nivel: {self.nivel_actual}"
            superficie_nivel = fuente.render(texto_nivel, True, BLANCO)
            self.pantalla.blit(superficie_nivel, (10, 10))

            # Mostrar robots restantes
            texto_robots = f"Robots: {len(self.robots)}"
            superficie_robots = fuente.render(texto_robots, True, BLANCO)
            self.pantalla.blit(superficie_robots, (10, 50))

            # Mostrar vidas
            for i in range(self.vidas):
                self.pantalla.blit(self.imagenes['vida'], (ANCHO_PANTALLA - 40 - i * 30, 10))

            # Mostrar indicaciones si todos los robots están eliminados
            if len(self.robots) == 0:
                fuente_indicacion = pygame.font.Font(None, 24)
                texto_indicacion = "¡Dirígete a la salida (cuadro verde)!"
                superficie_indicacion = fuente_indicacion.render(texto_indicacion, True, BLANCO)
                rect_indicacion = superficie_indicacion.get_rect(center=(ANCHO_PANTALLA // 2, 30))
                self.pantalla.blit(superficie_indicacion, rect_indicacion)

        # Dibujar menú si estamos en el estado de menú o pausa
        if self.estado_juego in ["menu", "pausa"]:
            self.menu.dibujar()

        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        pygame.quit()

