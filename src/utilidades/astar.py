import pygame
from src.constantes import *

class ListaPrioridad:
    """Implementación de una cola de prioridad"""
    def __init__(self):
        self.lista = []

    def push(self, item):
        """Agrega un elemento y mantiene la propiedad de montículo"""
        self.lista.append(item)
        self._sift_up(len(self.lista) - 1)

    def pop(self):
        """Elimina y retorna el elemento con menor valor f"""
        if not self.lista:
            return None
        if len(self.lista) == 1:
            return self.lista.pop()

        resultado = self.lista[0]
        self.lista[0] = self.lista.pop()
        if self.lista:
            self._sift_down(0)
        return resultado

    def _sift_up(self, pos):
        """Mueve un elemento hacia arriba en el montículo"""
        item = self.lista[pos]
        while pos > 0:
            padre_pos = (pos - 1) >> 1
            padre = self.lista[padre_pos]
            if item.f >= padre.f:
                break
            self.lista[pos] = padre
            pos = padre_pos
        self.lista[pos] = item


    def _sift_down(self, pos):
        """Mueve un elemento hacia abajo en el montículo"""
        item = self.lista[pos]
        n = len(self.lista)
        
        while True:
            hijo_izq = (pos << 1) + 1
            if hijo_izq >= n:
                break
            hijo_menor = hijo_izq
            hijo_der = hijo_izq + 1
            
            if hijo_der < n and self.lista[hijo_der].f < self.lista[hijo_izq].f:
                hijo_menor = hijo_der
            
            if item.f <= self.lista[hijo_menor].f:
                break
            
            self.lista[pos] = self.lista[hijo_menor]
            pos = hijo_menor
        self.lista[pos] = item
        
    def esta_vacia(self):
        return len(self.lista) == 0

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


    def esta_en_lista_cerrada(self, nodo, lista_cerrada):
       return any(n.x == nodo.x and n.y == nodo.y for n in lista_cerrada)

    def encontrar_nodo_en_lista(self, nodo, lista):
        for n in lista.lista: # Accedemos a la lista interna
            if n.x == nodo.x and n.y == nodo.y:
                return n
        return None

    def encontrar_ruta(self, inicio_x, inicio_y, objetivo_x, objetivo_y):
        """Encuentra una ruta usando el algoritmo A*"""
        # Convertir coordenadas de píxeles a coordenadas de cuadrícula
        inicio_x = inicio_x // self.tamano_celda
        inicio_y = inicio_y // self.tamano_celda
        objetivo_x = objetivo_x // self.tamano_celda
        objetivo_y = objetivo_y // self.tamano_celda
    

        # Crear nodos de inicio y objetivo
        inicio = Nodo(inicio_x, inicio_y)
        objetivo = Nodo(objetivo_x, objetivo_y)

        # Inicializar nodo de inicio
        inicio.g = 0
        inicio.h = self.distancia_manhattan(inicio, objetivo)
        inicio.f = inicio.g + inicio.h

        # Lista abierta (nodos por explorar) y lista cerrada (nodos explorados)
        lista_abierta = ListaPrioridad()
        lista_abierta.push(inicio)
        lista_cerrada = []
        
        while not lista_abierta.esta_vacia():
            actual = lista_abierta.pop()

            # Si llegamos al objetivo
            if actual == objetivo:
                ruta = []
                while actual:
                    # Convertir de vuelta a coordenadas de píxeles
                    ruta.append((
                        actual.x * self.tamano_celda + self.tamano_celda // 2,
                        actual.y * self.tamano_celda + self.tamano_celda // 2
                    ))
                    actual = actual.padre
                return ruta[::-1]  # Invertir la ruta

            lista_cerrada.append(actual)

            # Explorar vecinos
            for vecino in self.obtener_vecinos(actual):
                # Ignorar si ya está en la lista cerrada
                if self.esta_en_lista_cerrada(vecino, lista_cerrada):
                    continue

                nuevo_g = actual.g + 1

                # Buscar en lista abierta
                nodo_existente = self.encontrar_nodo_en_lista(vecino, lista_abierta)
                if not nodo_existente:
                    vecino.g = nuevo_g
                    vecino.h = self.distancia_manhattan(vecino, objetivo)
                    vecino.f = vecino.g + vecino.h
                    vecino.padre = actual
                    lista_abierta.push(vecino)
                elif nuevo_g < nodo_existente.g:
                    nodo_existente.g = nuevo_g
                    nodo_existente.f = nuevo_g + nodo_existente.h
                    nodo_existente.padre = actual

        return []  # No se encontró ruta

    def actualizar_obstaculo(self, x, y, es_obstaculo):
        """Actualiza la cuadrícula con un obstáculo"""
        celda_x = x // self.tamano_celda
        celda_y = y // self.tamano_celda
        if 0 <= celda_x < self.columnas and 0 <= celda_y < self.filas:
            self.cuadricula[celda_y][celda_x] = 1 if es_obstaculo else 0