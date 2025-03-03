import pygame
from src.constantes import *

def detectar_colision_balas_entidad(balas, entidad):
    #Detecta si alguna de las balas colisiona con la entidad.
    
    for bala in balas[:]:
        if bala.cuadrado.colliderect(entidad.cuadrado):
            balas.remove(bala)  # Eliminar la bala que colisionó
            return True
    return False

def detectar_colision_entidades(entidad1, entidad2):
    #Detecta si dos entidades colisionan.
    return entidad1.cuadrado.colliderect(entidad2.cuadrado)