import pygame
import math
from src.constantes import *
from src.entidades.bala import Bala
from src.utilidades.astar import AEstrella
from src.utilidades.arbol_comportamiento import Secuencia, Selector, PerseguirJugador


class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = ANCHO_JUGADOR #usar el mismo que el jugador
        self.alto = ALTO_JUGADOR
        self.velocidad = 1 #mas lento que el jugador
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.color = VERDE
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = 120 # mas lento que el jugador
        self.tiempo_antes_disparar = 180  # 3 segundos 
        self.puede_disparar = False
        self.velocidad_bala = 5 

        # Variables para A*
        self.navegador = AEstrella()
        self.ruta_actual = []
        self.punto_actual_indice = 0
        self.direccion_actual_x = 0
        self.direccion_actual_y = 0

        # Árbol de comportamiento
        self.arbol_comportamiento = Secuencia([
            PerseguirJugador()
        ])

    def actualizar_direccion(self, jugador_x, jugador_y):
        # Obtener nueva ruta
        nueva_ruta = self.navegador.encontrar_ruta(
            int(self.x), int(self.y),
            int(jugador_x), int(jugador_y)
        )
        
        if nueva_ruta and len(nueva_ruta) > 1:

            # Guardar la ruta para visualización
            self.ruta_actual = nueva_ruta

            # Calcular la dirección basada en el primer punto de la nueva ruta
            siguiente_punto = nueva_ruta[1]  # Usar el segundo punto para evitar giros bruscos
            dx = siguiente_punto[0] - self.x
            dy = siguiente_punto[1] - self.y      
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia != 0:
                self.direccion_actual_x = dx / distancia
                self.direccion_actual_y = dy / distancia

    def mover_hacia_jugador(self, jugador_x, jugador_y):
        # Actualizar dirección basada en la nueva posición del jugador
        self.actualizar_direccion(jugador_x, jugador_y)
        
        # Continuar movimiento en la dirección actual
        if self.direccion_actual_x != 0 or self.direccion_actual_y != 0:
            nueva_x = self.x + self.direccion_actual_x * self.velocidad
            nueva_y = self.y + self.direccion_actual_y * self.velocidad
            
            # Verificar límites de la pantalla
            nueva_x = max(0, min(nueva_x, ANCHO_PANTALLA - self.ancho))
            nueva_y = max(0, min(nueva_y, ALTO_PANTALLA - self.alto))
            
            self.x = nueva_x
            self.y = nueva_y
            self.cuadrado.x = self.x
            self.cuadrado.y = self.y

    def disparar_a_jugador(self, jugador_x, jugador_y):
        if not self.puede_disparar:
            return        
        
        if self.tiempo_recarga <= 0:
            # Calcular la dirección hacia el jugador
            dx = jugador_x - self.x
            dy = jugador_y - self.y

            # Normalizar la dirección
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia != 0:
                dx /= distancia
                dy /= distancia

                # crear la bala desde el centro del robot
                bala_x = self.x + self.ancho // 2 - ANCHO_BALA // 2
                bala_y = self.y + self.alto // 2 - ALTO_BALA // 2

                # Crear bala con velocidad personalizada
                bala = Bala(bala_x, bala_y, dx, dy)
                bala.velocidad = self.velocidad_bala  # Sobreescribir la velocidad de la bala
                self.balas.append(bala)
                self.tiempo_recarga = self.retraso_disparo
            
    def actualizar(self, jugador_x, jugador_y):
        # Reduce el tiempo de espera antes de que el robot pueda disparar
        if self.tiempo_antes_disparar > 0:
            self.tiempo_antes_disparar -= 1
            if self.tiempo_antes_disparar <= 0:
                self.puede_disparar = True       

        # Actualizar tiempo de recarga
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1
        
        #mover hacia el jugador
      #  self.mover_hacia_jugador(jugador_x, jugador_y)

        # Ejecutar árbol de comportamiento
        self.arbol_comportamiento.ejecutar(self, jugador_x, jugador_y)

        #Intentar disparar
        self.disparar_a_jugador(jugador_x, jugador_y)

        # Actualizar balas
        for bala in self.balas[:]:
            bala.actualizar()
            if bala.esta_fuera_pantalla():
                self.balas.remove(bala)


    def dibujar(self, surface):
        # Dibujar la ruta (para depuración)
        if self.ruta_actual:
            for i in range(len(self.ruta_actual) - 1):
                pygame.draw.line(surface, (255, 0, 0), 
                               self.ruta_actual[i], 
                               self.ruta_actual[i + 1], 1)

        pygame.draw.rect(surface, self.color, self.cuadrado)
        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(surface)
