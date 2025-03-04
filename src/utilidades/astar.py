import pygame
from src.constantes import *

class Nodo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float('inf')  # costo desde el inicio
        self.h = 0  # Heurística (distancia estimada al objetivo)
        self.f = float('inf')  # f = g + h
        self.padre = None

    def __eq__(self, otro):
        if otro is None:
            return False
        return self.x == otro.x and self.y == otro.y

class AEstrella:
    def __init__(self, tamano_celda=32):
        self.tamano_celda = tamano_celda
        self.filas = ALTO_PANTALLA // tamano_celda
        self.columnas = ANCHO_PANTALLA // tamano_celda
        self.reiniciar_cuadricula()

    def reiniciar_cuadricula(self):
        # Reinicia la cuadrícula para un nuevo cálculo de ruta
        self.cuadricula = []
        for _ in range(self.filas):
            fila = [0] * self.columnas
            self.cuadricula.append(fila)

