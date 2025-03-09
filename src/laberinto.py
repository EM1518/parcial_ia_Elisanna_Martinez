# src/laberinto.py
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
        Dibuja la pared en la superficie proporcionada
        """
        pygame.draw.rect(superficie, self.color, self.cuadrado)

class Laberinto:
    """
    Clase que gestiona la estructura del laberinto, incluyendo sus paredes
    """
    def __init__(self):
        self.paredes = []
        self.crear_primer_laberinto()
        
    def crear_primer_laberinto(self):
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
        # Pared horizontal superior izquierda
        self.paredes.append(Pared(0, 200, 180, grosor))
        
        # Pared vertical central superior
        self.paredes.append(Pared(350, 0, grosor, 230))
        
        # Pared horizontal central
        self.paredes.append(Pared(180, 350, 300, grosor))
        
        # Pared vertical central
        self.paredes.append(Pared(350, 230, grosor, 120))
        
        # Pared vertical derecha
        self.paredes.append(Pared(600, 230, grosor, 250))
        
        # Pared horizontal inferior izquierda
        self.paredes.append(Pared(0, 430, 180, grosor))
        
        # Pared vertical izquierda inferior
        self.paredes.append(Pared(180, 350, grosor, 150))
        
    def dibujar(self, superficie):
        """
        Dibuja todas las paredes del laberinto
        """
        for pared in self.paredes:
            pared.dibujar(superficie)
            
    def verificar_colision(self, cuadrado):
        """
        Verifica si un cuadrado colisiona con alguna pared del laberinto
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