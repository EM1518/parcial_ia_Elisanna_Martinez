import pygame
from src.constantes import *

class Pared:
    """
    Clase que representa una pared en el laberinto
    """
    def __init__(self, x, y, ancho, alto):
        self.cuadrado = pygame.Rect(x, y, ancho, alto)
        self.color = AZUL  # Color azul para las paredes

    def dibujar(self, superficie):
        """
        Dibuja la pared en la superficie
        """
        pygame.draw.rect(superficie, self.color, self.cuadrado)

class Laberinto:
    """
    Clase que gestiona la estructura del laberinto, incluyendo sus paredes
    """
    def __init__(self, nivel=1):
        self.paredes = []
        self.nivel = nivel
        self.crear_laberinto(nivel)

    def crear_laberinto(self, nivel):
        """
        Crea el laberinto según el nivel especificado
        """
        self.paredes.clear()
        if nivel == 1:
            self.crear_primer_nivel()
        elif nivel == 2:
            self.crear_segundo_nivel()
        elif nivel == 3:
            self.crear_tercer_nivel()

    def crear_primer_nivel(self):
        """
        Crea el primer nivel del laberinto
        """
        grosor = 10  # Grosor de las paredes
        
        # Paredes exteriores
        # Pared superior
        self.paredes.append(Pared(0, 0, ANCHO_PANTALLA, grosor))
        # Pared inferior
        self.paredes.append(Pared(0, ALTO_PANTALLA - grosor, ANCHO_PANTALLA, grosor))
        # Pared izquierda
        self.paredes.append(Pared(0, 0, grosor, ALTO_PANTALLA))
        # Pared derecha
        self.paredes.append(Pared(ANCHO_PANTALLA - grosor, 0, grosor, ALTO_PANTALLA))

        # Paredes interiores
        # Pared vertical central
        self.paredes.append(Pared(400, 0, grosor, 300))

        # Pared horizontal superior izquierda
        self.paredes.append(Pared(0, 200, 200, grosor))

        # Pared horizontal central
        self.paredes.append(Pared(215, 480, 370, grosor))

        # Pared vertical derecha
        self.paredes.append(Pared(600, 300, grosor, 300))

        # Pared vertical pequeña inferior
        self.paredes.append(Pared(215, 350, grosor, 130))


    def crear_segundo_nivel(self):
        """
        Crea el segundo nivel
        """
        grosor = 10  # Grosor de las paredes

        # Paredes exteriores
        self.paredes.append(Pared(0, 0, ANCHO_PANTALLA, grosor))
        self.paredes.append(Pared(0, ALTO_PANTALLA - grosor, ANCHO_PANTALLA, grosor))
        self.paredes.append(Pared(0, 0, grosor, ALTO_PANTALLA))
        self.paredes.append(Pared(ANCHO_PANTALLA - grosor, 0, grosor, ALTO_PANTALLA))

        # Pared horizontal central con amplia apertura
        self.paredes.append(Pared(0, 300, 300, grosor))  # Sección izquierda
        self.paredes.append(Pared(500, 300, 300, grosor))  # Sección derecha

        # Pared vertical central con amplia apertura
        self.paredes.append(Pared(400, 0, grosor, 200))  # Sección superior
        self.paredes.append(Pared(400, 400, grosor, 200))  # Sección inferior

        # Sección superior izquierda - una pequeña extensión vertical
        self.paredes.append(Pared(200, 0, grosor, 150))

        # Sección superior derecha - una pequeña extensión horizontal
        self.paredes.append(Pared(550, 150, 250, grosor))

        # Sección inferior izquierda - una pequeña barrera horizontal
        self.paredes.append(Pared(150, 450, 150, grosor))

        # Sección inferior derecha - una pequeña extensión vertical
        self.paredes.append(Pared(600, 350, grosor, 150))

    def crear_tercer_nivel(self):
        """
        Crea el tercer nivel del laberinto
        """
        grosor = 10  # Grosor de las paredes

        # Paredes exteriores
        self.paredes.append(Pared(0, 0, ANCHO_PANTALLA, grosor))
        self.paredes.append(Pared(0, ALTO_PANTALLA - grosor, ANCHO_PANTALLA, grosor))
        self.paredes.append(Pared(0, 0, grosor, ALTO_PANTALLA))
        self.paredes.append(Pared(ANCHO_PANTALLA - grosor, 0, grosor, ALTO_PANTALLA))


        # Paredes horizontales
        # Primera fila horizontal (superior)
        self.paredes.append(Pared(100, 100, 200, grosor))
        self.paredes.append(Pared(400, 100, 300, grosor))

        # Segunda fila horizontal
        self.paredes.append(Pared(200, 200, 400, grosor))

        # Tercera fila horizontal
        self.paredes.append(Pared(100, 300, 200, grosor))
        self.paredes.append(Pared(400, 300, 300, grosor))

        # Cuarta fila horizontal
        self.paredes.append(Pared(200, 400, 400, grosor))

        # Quinta fila horizontal
        self.paredes.append(Pared(100, 500, 200, grosor))
        self.paredes.append(Pared(400, 500, 300, grosor))

        # Paredes verticales
        # Primera columna vertical (izquierda)
        self.paredes.append(Pared(100, 100, grosor, 100))
        self.paredes.append(Pared(100, 300, grosor, 100))

        # Segunda columna vertical
        self.paredes.append(Pared(200, 200, grosor, 100))
        self.paredes.append(Pared(200, 400, grosor, 100))

        # Tercera columna vertical
        self.paredes.append(Pared(400, 100, grosor, 100))
        self.paredes.append(Pared(400, 300, grosor, 100))

        # Cuarta columna vertical
        self.paredes.append(Pared(600, 200, grosor, 100))
        self.paredes.append(Pared(600, 400, grosor, 100))

        # Obstáculos adicionales
        self.paredes.append(Pared(300, 150, grosor, 50))
        self.paredes.append(Pared(500, 350, grosor, 50))
        self.paredes.append(Pared(300, 450, 50, grosor))
        self.paredes.append(Pared(450, 250, 50, grosor))

    def cambiar_nivel(self, nivel):
        """
        Cambia al nivel especificado
        """
        if 1 <= nivel <= 3:
            self.nivel = nivel
            self.crear_laberinto(nivel)
            return True
        return False

    def siguiente_nivel(self):
        """
        Avanza al siguiente nivel
        """
        if self.nivel < 3:
            self.nivel += 1
            self.crear_laberinto(self.nivel)
            return True
        return False

    def verificar_colision_amplia(self, cuadrado):
        """
        Verifica si un elemento está cerca de alguna pared del laberinto
        Retorna True si hay colisión cercana, False en caso contrario
        """
        # Para cada pared, verificar si está cerca del elemento
        for pared in self.paredes:
            # Verificamos si hay intersección directa
            if pared.cuadrado.colliderect(cuadrado):
                return True
        return False
    def dibujar(self, superficie):
        """
        Dibuja todas las paredes del laberinto
        """
        for pared in self.paredes:
            pared.dibujar(superficie)
            
    def verificar_colision(self, cuadrado):
        """
        Verifica si un elemento colisiona con alguna pared del laberinto
        Retorna True si hay colisión, False en caso contrario
        """
        for pared in self.paredes:
            if pared.cuadrado.colliderect(cuadrado):
                return True
        return False
    
    def obtener_paredes_para_astar(self):
        """
        Retorna una lista de cuadrados de las paredes para el algoritmo A*
        """
        return [pared.cuadrado for pared in self.paredes]