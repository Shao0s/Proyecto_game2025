import pygame , sys
from pygame.locals import*

# Inicializar todos los módulos de pygame
pygame.init()

# Crear la ventana (ancho, alto)
ventana = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Mi primer juego con Pygame")
    # Rellenar la pantalla con un color (RGB)
ventana.fill((255, 255, 255))  # Blanco

# Bucle principal del juego
while True:
    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:  # Si cierras la ventana
            sys.exit()

    # Actualizar toda la pantalla
    pygame.display.flip()

