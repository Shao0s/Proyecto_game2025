import pygame , sys
import os
from pygame.locals import*

# Inicializar todos los módulos de pygame
pygame.init()

# Crear la ventana (ancho, alto)
ventana = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Secretos del Reino Hundido")

#Pantalla de inicio
pantalla_carga = pygame.image.load("imagenes/inicio.png")
ventana.blit(pantalla_carga, (0,0))

#Musica de fondo
pygame.mixer_music.load('sonido/Jeremy_Korpas.ogg')
pygame.mixer_music.play(-1)    # -1 se repite la cancion indefinidamente

# Sonido
#sonido_arriba = pygame.image.load('sonido/sonido_arriba.png')
sonido_abajo = pygame.image.load('sonido/sonido_abajo.png')
sonido_mute = pygame.image.load('sonido/sonido_mute.png')
#sonido_max = pygame.image.load('sonido/sonido_max.png')

# Fuente para el texto
fuente = pygame.font.Font(None, 50)  # Fuente por defecto tamaño 50

# Variables para controlar escenas
ESCENA_INICIO = 0
ESCENA_JUEGO = 1
escena_actual = ESCENA_INICIO

# Reloj para controlar FPS y parpadeo
reloj = pygame.time.Clock()

# Bucle principal del juego
while True:
    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:  # Si cierras la ventana
            sys.exit()

    #Opcion tecla pulsada
    keys = pygame.key.get_pressed()

    # ===== ESCENA DE INICIO =====
    if escena_actual == ESCENA_INICIO:
        ventana.blit(pantalla_carga, (0, 0))

        # Texto intermitente
        tiempo = pygame.time.get_ticks() // 500  # cada medio segundo cambia
        if tiempo % 2 == 0:
            texto = fuente.render("Presiona ENTER para continuar", True, (255, 255, 255))
            ventana.blit(texto, (160, 500))  # posición del texto

        # Si presiona ENTER -> cambiar de escena
        if keys[pygame.K_RETURN]:
            escena_actual = ESCENA_JUEGO

        # ===== ESCENA DEL JUEGO =====
    elif escena_actual == ESCENA_JUEGO:
        ventana.fill((0, 0, 0))  # Fondo negro (puedes poner tu fondo del juego)

        # Ejemplo: mostrar un texto de "Juego iniciado"
        texto_juego = fuente.render("¡Bienvenido al Reino Hundido!", True, (200, 200, 0))
        ventana.blit(texto_juego, (150, 250))

    # Bajar volumen
    if keys[pygame.K_9] and pygame.mixer.music.get_volume() > 0.0:  #get obtener valores
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.01)
        ventana.blit(sonido_abajo, (690, 5))
    elif keys[pygame.K_9] and pygame.mixer.music.get_volume() == 0.0:
        ventana.blit(sonido_mute, (690, 5))

    #Sube volumen
    if keys[pygame.K_0] and pygame.mixer.music.get_volume() < 1.0:
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.01)
        ventana.blit(sonido_arriba, (690, 5))
    elif keys[pygame.K_0] and pygame.mixer.music.get_volume() == 1.0:
        ventana.blit(sonido_max, (690, 5))

    ##Desactivar sonido
    elif keys[pygame.K_m]:
        pygame.mixer.music.set_volume(0.0)
        ventana.blit(sonido_mute, (690, 5))

    #Activar sonido
    elif keys[pygame.K_COMMA]:
        pygame.mixer.music.set_volume(1.0)
        ventana.blit(sonido_mute, (690, 5))


        # Actualizar toda la pantalla
    pygame.display.flip()
