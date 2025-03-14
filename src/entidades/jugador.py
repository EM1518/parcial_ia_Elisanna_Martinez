# Elisanna María Martínez Sánchez 23-EISN-2-074

import pygame
import os
import math
from src.constantes import *
from src.entidades.bala import Bala

#Clase para el jugador
class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ultima_x = x
        self.ultima_y = y
        self.ancho = ANCHO_JUGADOR
        self.alto = ALTO_JUGADOR
        self.velocidad = VELOCIDAD_JUGADOR
        self.cuadrado = pygame.Rect(x, y, self.ancho, self.alto)
        self.balas = []
        self.tiempo_recarga = 0
        self.retraso_disparo = RETRASO_DISPARO_JUGADOR # Frames de delay
        self.color = VERDE
        self.dx = 0
        self.dy = 0

        # Cargar sprites
        self.cargar_sprites()

    def mover(self, dx, dy):
        """
        Guarda la dirección del movimiento para ser aplicada en actualizar()
        """
        self.dx = dx
        self.dy = dy

    def retroceder(self):
        """
        Retroceder a la última posición válida después de una colisión
        """
        self.x = self.ultima_x
        self.y = self.ultima_y
        self.cuadrado.x = round(self.x)
        self.cuadrado.y = round(self.y)

    def disparar(self, dx, dy):
        if self.tiempo_recarga <= 0:
            bala_x = self.x + self.ancho // 2 - ANCHO_BALA // 2
            bala_y = self.y + self.alto // 2 - ALTO_BALA // 2

            nueva_bala = Bala(bala_x, bala_y, dx, dy)
            nueva_bala.velocidad = VELOCIDAD_BALA  # Usar la constante para la velocidad de la bala

            self.balas.append(nueva_bala)
            self.tiempo_recarga = self.retraso_disparo

    def actualizar(self, laberinto=None):
        """
        Actualiza la posición y estado del jugador
        """
        # Guardar posición anterior para colisiones
        self.ultima_x = self.x
        self.ultima_y = self.y

        # Calcular nueva posición basada en dx y dy
        if self.dx != 0 or self.dy != 0:
            # Normalizar el movimiento diagonal
            if self.dx != 0 and self.dy != 0:
                self.dx *= 0.7071  # 1/√2
                self.dy *= 0.7071

            # Aplicar velocidad
            self.x += self.dx * self.velocidad
            self.y += self.dy * self.velocidad

            # Actualizar animación si hay sprites
            if self.usar_sprites:
                self.frame_contador += 1
                if self.frame_contador < 7:
                    self.sprite_actual = 'movimiento1'
                elif self.frame_contador < 14:
                    self.sprite_actual = 'movimiento2'
                elif self.frame_contador < 21:
                    self.sprite_actual = 'movimiento3'
                else:
                    self.frame_contador = 0
        else:
            self.sprite_actual = 'estatico'

        # Mantener dentro de los límites de la pantalla
        self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ancho))
        self.y = max(0, min(self.y, ALTO_PANTALLA - self.alto))

        # Actualizar el cuadrado de colisión
        self.cuadrado.x = round(self.x)
        self.cuadrado.y = round(self.y)

        # Actualizar cooldown de disparo
        if self.tiempo_recarga > 0:
            self.tiempo_recarga -= 1

        # Actualizar balas
        for bala in self.balas[:]:
            # Si la bala colisiona con una pared, eliminarla
            if laberinto and bala.actualizar(laberinto):
                self.balas.remove(bala)
            elif bala.esta_fuera_pantalla():
                self.balas.remove(bala)

    def dibujar(self, surface):
        if self.usar_sprites:
            surface.blit(self.sprites[self.sprite_actual], self.cuadrado)
        else:
            pygame.draw.rect(surface, self.color, self.cuadrado)

        # Dibujar balas
        for bala in self.balas:
            bala.dibujar(surface)

    def cargar_sprites(self):
        """Carga los sprites del jugador"""
        # Cargar sprites
        self.sprites = {}
        try:
            self.sprites['estatico'] = pygame.transform.scale(
                pygame.image.load(os.path.join('assets', 'imagenes', 'jugador', 'jugador_estatico.png')),
                (self.ancho, self.alto))
            self.sprites['movimiento1'] = pygame.transform.scale(
                pygame.image.load(os.path.join('assets', 'imagenes', 'jugador', 'jugador_movimiento1.png')),
                (self.ancho, self.alto))
            self.sprites['movimiento2'] = pygame.transform.scale(
                pygame.image.load(os.path.join('assets', 'imagenes', 'jugador', 'jugador_movimiento2.png')),
                (self.ancho, self.alto))
            self.sprites['movimiento3'] = pygame.transform.scale(
                pygame.image.load(os.path.join('assets', 'imagenes', 'jugador', 'jugador_movimiento3.png')),
                (self.ancho, self.alto))
            self.usar_sprites = True
        except Exception as e:
            print(f"Error al cargar sprites del jugador: {e}")
            self.usar_sprites = False

        self.sprite_actual = 'estatico'
        self.frame_contador = 0