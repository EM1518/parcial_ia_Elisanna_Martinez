# Elisanna María Martínez Sánchez 23-EISN-2-074

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
        self.obstaculos = []  # Lista para almacenar obstáculos
        self.tiempo_ultima_busqueda = 0
        self.ultima_ruta = []

    def reiniciar_cuadricula(self):
        # Reinicia la cuadrícula para un nuevo cálculo de ruta
        self.cuadricula = []
        for _ in range(self.filas):
            fila = [0] * self.columnas
            self.cuadricula.append(fila)

    def actualizar_obstaculos(self, obstaculos):
        """
        Actualiza la lista de obstáculos y la cuadrícula de navegación
        """
        self.obstaculos = obstaculos
        self.reiniciar_cuadricula()

        # Un margen pequeño
        margen = 0.3

        # Marcar las celdas que contienen obstáculos
        for obstaculo in self.obstaculos:
            # Calcular las celdas que cubre el obstáculo
            celda_x1 = max(0, int((obstaculo.x - margen * self.tamano_celda) // self.tamano_celda))
            celda_y1 = max(0, int((obstaculo.y - margen * self.tamano_celda) // self.tamano_celda))
            celda_x2 = min(self.columnas - 1,
                           int((obstaculo.x + obstaculo.width + margen * self.tamano_celda) // self.tamano_celda))
            celda_y2 = min(self.filas - 1,
                           int((obstaculo.y + obstaculo.height + margen * self.tamano_celda) // self.tamano_celda))

            # Marcar todas las celdas cubiertas por el obstáculo
            for y in range(celda_y1, celda_y2 + 1):
                for x in range(celda_x1, celda_x2 + 1):
                    if 0 <= y < self.filas and 0 <= x < self.columnas:
                        self.cuadricula[y][x] = 1  # 1 indica obstáculo

    def obtener_vecinos(self, nodo):
      # Obtiene los nodos vecinos válidos
        vecinos = []
        direcciones = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinales
            (1, 1), (-1, 1), (-1, -1), (1, -1)  # Diagonales
        ]
        for dx, dy in direcciones:
            nuevo_x = int(nodo.x + dx)
            nuevo_y = int(nodo.y + dy)

            if (0 <= nuevo_x < self.columnas and 0 <= nuevo_y < self.filas):
                if dx != 0 and dy != 0:
                    if self.cuadricula[nuevo_y][int(nodo.x)] >= 1 or self.cuadricula[int(nodo.y)][nuevo_x] >= 1:
                        continue  # No permitir "cortar esquinas"

                # 0 = libre, 1 = obstáculo, 2 = zona de precaución
                if self.cuadricula[nuevo_y][nuevo_x] == 0:  # Solo si no hay obstáculo
                    vecinos.append(Nodo(nuevo_x, nuevo_y))
                elif self.cuadricula[nuevo_y][nuevo_x] == 2:  # Zona de precaución
                    # Permitir el paso, pero con un costo mayor
                    vecino = Nodo(nuevo_x, nuevo_y)
                    vecino.g = float('inf')
                    vecino.h = self.distancia_manhattan(vecino, objetivo) * 1.5  # Costo mayor
                    vecino.f = vecino.g + vecino.h
                    vecinos.append(vecino)

        return vecinos

    def distancia_manhattan(self, nodo, objetivo):
       # Calcula la distancia Manhattan entre dos nodos
        return abs(nodo.x - objetivo.x) + abs(nodo.y - objetivo.y)

    def esta_en_lista_cerrada(self, nodo, lista_cerrada):
       return any(n.x == nodo.x and n.y == nodo.y for n in lista_cerrada)

    def encontrar_nodo_en_lista(self, nodo, lista):
        for n in lista.lista: # Accede a la lista interna
            if n.x == nodo.x and n.y == nodo.y:
                return n
        return None

    def calcular_separacion(self, x, y, otros_robots, distancia_minima=60):
        """Calcula el vector de separación para evitar otros robots"""
        separacion_x = 0
        separacion_y = 0

        for otro_robot in otros_robots:
            # No calcular para sí mismo
            if x == otro_robot.x and y == otro_robot.y:
                continue

            dx = x - otro_robot.x
            dy = y - otro_robot.y
            distancia = (dx * dx + dy * dy) ** 0.5

            # Si está demasiado cerca, calcular vector de separación
            if distancia < distancia_minima and distancia > 0:
                fuerza = (distancia_minima - distancia) / distancia
                separacion_x += dx * fuerza
                separacion_y += dy * fuerza

        return separacion_x, separacion_y

    def encontrar_direccion(self, x_inicio, y_inicio, x_objetivo, y_objetivo, otros_robots=None):
        """
        Encuentra la dirección óptima hacia un objetivo, devolviendo un vector normalizado
        """
        ruta = self.encontrar_ruta(x_inicio, y_inicio, x_objetivo, y_objetivo)

        if not ruta or len(ruta) < 2:
            return 0, 0  # Sin dirección si no hay ruta

        # Obtener siguiente punto en la ruta
        siguiente_punto = ruta[1]
        dx = siguiente_punto[0] - x_inicio
        dy = siguiente_punto[1] - y_inicio

        distancia = (dx * dx + dy * dy) ** 0.5
        if distancia == 0:
            return 0, 0

        # Normalizar vector
        dx = dx / distancia
        dy = dy / distancia

        # Si hay robots para considerar, incluir separación
        if otros_robots:
            sep_x, sep_y = self.calcular_separacion(x_inicio, y_inicio, otros_robots)
            if sep_x != 0 or sep_y != 0:
                # Combinar dirección con separación
                factor_separacion = 0.5
                dx += sep_x * factor_separacion
                dy += sep_y * factor_separacion

                # Renormalizar el vector resultante
                magnitud = (dx * dx + dy * dy) ** 0.5
                if magnitud > 0:
                    dx /= magnitud
                    dy /= magnitud

        return dx, dy

    def verificar_camino_libre(self, x1, y1, x2, y2, laberinto=None):
        """Verifica si hay un camino libre entre dos puntos"""

        # Calcular la distancia entre los puntos
        distancia = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # Más puntos para distancias mayores
        num_pasos = max(10, int(distancia / 10))

        # Verificar varios puntos a lo largo de la ruta
        for i in range(num_pasos + 1):
            t = i / num_pasos
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t

            # Crear un rectángulo para verificar colisiones
            ancho_check = 20 + 5 * 2  # Ancho típico + margen
            alto_check = 30 + 5 * 2  # Alto típico + margen
            rect_check = pygame.Rect(x - ancho_check / 2, y - alto_check / 2, ancho_check, alto_check)
            if laberinto and laberinto.verificar_colision(rect_check):
                return False  # Hay un obstáculo en el camino
        return True  # No hay obstáculos en el camino

    def encontrar_ruta(self, inicio_x, inicio_y, objetivo_x, objetivo_y):
        """Encuentra una ruta usando el algoritmo A*"""

        # Limitar la frecuencia de búsqueda (cada 5 frames)
        self.tiempo_ultima_busqueda += 1
        if self.tiempo_ultima_busqueda < 5 and self.ultima_ruta:
            return self.ultima_ruta
        self.tiempo_ultima_busqueda = 0

        # Convertir coordenadas de píxeles a coordenadas de cuadrícula
        inicio_x = int(inicio_x // self.tamano_celda)
        inicio_y = int(inicio_y // self.tamano_celda)
        objetivo_x = int(objetivo_x // self.tamano_celda)
        objetivo_y = int(objetivo_y // self.tamano_celda)

        # Asegurar que las coordenadas están dentro de los límites
        inicio_x = max(0, min(inicio_x, self.columnas - 1))
        inicio_y = max(0, min(inicio_y, self.filas - 1))
        objetivo_x = max(0, min(objetivo_x, self.columnas - 1))
        objetivo_y = max(0, min(objetivo_y, self.filas - 1))

        # Si el objetivo está en un obstáculo, buscar la celda libre más cercana
        if self.cuadricula[objetivo_y][objetivo_x] == 1:
            mejor_distancia = float('inf')
            mejor_x, mejor_y = objetivo_x, objetivo_y

            # Buscar en un radio de 5 celdas
            for y in range(max(0, objetivo_y - 5), min(self.filas, objetivo_y + 6)):
                for x in range(max(0, objetivo_x - 5), min(self.columnas, objetivo_x + 6)):
                    if self.cuadricula[y][x] == 0:
                        distancia = abs(x - objetivo_x) + abs(y - objetivo_y)
                        if distancia < mejor_distancia:
                            mejor_distancia = distancia
                            mejor_x, mejor_y = x, y
            objetivo_x, objetivo_y = mejor_x, mejor_y

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

        # Limitar el número de iteraciones para evitar bucles infinitos
        max_iteraciones = 200
        iteraciones = 0
        mejor_nodo = inicio  # Mejor nodo encontrado hasta ahora
        mejor_distancia = inicio.h
        
        while not lista_abierta.esta_vacia() and iteraciones < max_iteraciones:
            iteraciones += 1
            actual = lista_abierta.pop()

            if actual.h < mejor_distancia:
                mejor_nodo = actual
                mejor_distancia = actual.h

            # Si llega al objetivo
            if actual == objetivo:
                ruta = []
                while actual:
                    # Convertir de vuelta a coordenadas de píxeles
                    ruta.append((
                        actual.x * self.tamano_celda + self.tamano_celda // 2,
                        actual.y * self.tamano_celda + self.tamano_celda // 2
                    ))
                    actual = actual.padre
                self.ultima_ruta = ruta[::-1]
                return self.ultima_ruta

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

        # Si no encuentra ruta, usar el mejor nodo encontrado
        if mejor_nodo != inicio:
            ruta = []
            actual = mejor_nodo
            while actual:
                ruta.append((
                    actual.x * self.tamano_celda + self.tamano_celda // 2,
                    actual.y * self.tamano_celda + self.tamano_celda // 2
                ))
                actual = actual.padre

            self.ultima_ruta = ruta[::-1]
            return self.ultima_ruta

        # Si no hay ruta posible, retornar una ruta directa
        self.ultima_ruta = [
            (inicio_x * self.tamano_celda + self.tamano_celda // 2,
            inicio_y * self.tamano_celda + self.tamano_celda // 2),
            (objetivo_x * self.tamano_celda + self.tamano_celda // 2,
            objetivo_y * self.tamano_celda + self.tamano_celda // 2)
        ]
        return self.ultima_ruta