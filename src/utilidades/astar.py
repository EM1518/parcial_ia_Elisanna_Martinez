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


    def obtener_vecinos(self, nodo):
      # Obtiene los nodos vecinos válidos
        vecinos = []
        # 4 direcciones principales: arriba, derecha, abajo, izquierda
        direcciones = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in direcciones:
            nuevo_x = nodo.x + dx
            nuevo_y = nodo.y + dy

            if (0 <= nuevo_x < self.columnas and 
                0 <= nuevo_y < self.filas and 
                self.cuadricula[nuevo_y][nuevo_x] == 0):
                vecinos.append(Nodo(nuevo_x, nuevo_y))
        return vecinos

    def distancia_manhattan(self, nodo, objetivo):
       # Calcula la distancia Manhattan entre dos nodos
        return abs(nodo.x - objetivo.x) + abs(nodo.y - objetivo.y)

    def encontrar_menor_f(self, lista_abierta):
        # Encuentra el nodo con menor valor f en la lista abierta
        menor_f = float('inf')
        nodo_menor = None
        indice_menor = 0
        
        for i, nodo in enumerate(lista_abierta):
            if nodo.f < menor_f:
                menor_f = nodo.f
                nodo_menor = nodo
                indice_menor = i
                
        if nodo_menor:
            lista_abierta.pop(indice_menor)
        return nodo_menor


    def esta_en_lista(self, nodo, lista):
        # Verifica si un nodo está en una lista
        for n in lista:
            if n == nodo:
                return n
        return None


