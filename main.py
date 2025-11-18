import pygame, sys, time, os
from pygame.locals import *
from db import (
    cargar_perfiles, crear_perfil, borrar_perfil,
    guardar_tiempo, cargar_perfil, cerrar_bd
)

# Asegurar ruta correcta
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init()

ventana = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Secretos del Reino Hundido")

fuente = pygame.font.Font(None, 36)

# ------------------------------
#   FONDOS
# ------------------------------
fondos = {
    "inicio": pygame.image.load("imagenes/inicio.png"),
    "menu": pygame.image.load("imagenes/menu.png"),
    "escena_1": pygame.image.load("imagenes/escena_1.png")
}

# ------------------------------
#   ESCENAS
# ------------------------------
ESCENA_INICIO = 0
ESCENA_PERFILES = 1
ESCENA_CREAR_PERFIL = 2
ESCENA_JUEGO = 3

escena_actual = ESCENA_INICIO
perfil_pointer = 0
perfil_seleccionado = None

reloj = pygame.time.Clock()
ultimo_guardado = time.time()

# ------------------------------
#   musica
# ------------------------------
pygame.mixer.music.load("sonido/Jeremy_Korpas.ogg")
pygame.mixer.music.play(-1)
#efectos de sonido
enter_sfx = pygame.mixer.Sound("sonido/enter.ogg")

# Iconos de volumen
sonido_arriba = pygame.image.load('sonido/sonido_arriba.png')
sonido_abajo = pygame.image.load('sonido/sonido_abajo.png')
sonido_mute = pygame.image.load('sonido/sonido_mute.png')
sonido_max = pygame.image.load('sonido/sonido_max.png')
sonido_act = pygame.image.load('sonido/sonido_act.png')

icono_volumen = None

# ------------------------------
#   NOMBRE TEMPORAL
# ------------------------------
nombre_temporal = ""

# ------------------------------
#   FORMATEAR TIEMPO
# ------------------------------
def formatear_tiempo(segundos):
    segundos = int(segundos)
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    return f"{horas:02d}h {minutos:02d}m"


# ------------------------------
#   TRANSICIÓN
# ------------------------------
def transicion(ventana, duracion=700):
    ancho, alto = ventana.get_size()
    centro = (ancho // 2, alto // 2)

    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    # Cierre circular
    for radio in range(max(ancho, alto), 0, -40):
        overlay.fill((0, 0, 0, 255))
        pygame.draw.circle(overlay, (0, 0, 0, 0), centro, radio)
        ventana.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.delay(duracion // 30)

    overlay.fill((0, 0, 0))
    ventana.blit(overlay, (0, 0))
    pygame.display.update()
    pygame.time.delay(100)

    # Apertura circular
    for radio in range(0, max(ancho, alto), 40):
        overlay.fill((0, 0, 0, 255))
        pygame.draw.circle(overlay, (0, 0, 0, 0), centro, radio)
        ventana.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.delay(duracion // 30)


# =======================================================
#   BUCLE PRINCIPAL
# =======================================================
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            cerrar_bd()
            sys.exit()

        if evento.type == KEYDOWN:

            # ------------------------------
            #  ESCENA INICIO
            # ------------------------------
            if escena_actual == ESCENA_INICIO:
                if evento.key == K_RETURN:
                    enter_sfx.play()
                    escena_actual = ESCENA_PERFILES

            # ------------------------------
            #  ESCENA PERFILES
            # ------------------------------
            elif escena_actual == ESCENA_PERFILES:

                if evento.key == K_UP:
                    perfil_pointer = max(0, perfil_pointer - 1)

                elif evento.key == K_DOWN:
                    perfil_pointer = min(1, perfil_pointer + 1)

                elif evento.key == K_RETURN:
                    enter_sfx.play()
                    perfiles = cargar_perfiles()
                    pid, nombre, *_ = perfiles[perfil_pointer]
                    perfil_seleccionado = pid

                    if nombre is None:
                        nombre_temporal = ""
                        escena_actual = ESCENA_CREAR_PERFIL
                    else:
                        # Transición
                        transicion(ventana)
                        escena_actual = ESCENA_JUEGO

                    ultimo_guardado = time.time()

                elif evento.key == K_b:
                    perfiles = cargar_perfiles()
                    pid, _, *_ = perfiles[perfil_pointer]
                    borrar_perfil(pid)

            # ------------------------------
            #  CREAR PERFIL
            # ------------------------------
            elif escena_actual == ESCENA_CREAR_PERFIL:

                # ENTER crea el perfil
                if evento.key == K_RETURN and nombre_temporal.strip() != "":
                    enter_sfx.play()

                    crear_perfil(
                        perfil_seleccionado,
                        nombre_temporal,
                        "Unico",
                        "imagenes/icono_default.png"
                    )

                    # Transición al entrar al juego
                    transicion(ventana)

                    escena_actual = ESCENA_JUEGO
                    ultimo_guardado = time.time()

                elif evento.key == K_BACKSPACE:
                    nombre_temporal = nombre_temporal[:-1]

                else:
                    if evento.unicode.isprintable() and len(nombre_temporal) < 15:
                        nombre_temporal += evento.unicode


    # ==================================================
    #  CONTROL DE VOLUMEN
    # ==================================================
    if escena_actual != ESCENA_CREAR_PERFIL:
        keys = pygame.key.get_pressed()

        # --------------------------
        #  BAJAR VOLUMEN (tecla 9)
        # --------------------------
        if keys[K_9]:
            vol = pygame.mixer.music.get_volume()
            vol = max(0.0, vol - 0.01)
            pygame.mixer.music.set_volume(vol)

            if vol == 0.0:
                icono_volumen = sonido_mute  # llegó a mínimo
            else:
                icono_volumen = sonido_abajo

        # --------------------------
        #  SUBIR VOLUMEN (tecla 0)
        # --------------------------
        if keys[K_0]:
            vol = pygame.mixer.music.get_volume()
            vol = min(1.0, vol + 0.01)
            pygame.mixer.music.set_volume(vol)

            if vol == 1.0:
                icono_volumen = sonido_max  # llegó al máximo
            else:
                icono_volumen = sonido_arriba

        # --------------------------
        #  MUTE (tecla M)
        # --------------------------
        if keys[K_m]:
            pygame.mixer.music.set_volume(0.0)
            icono_volumen = sonido_mute

        # --------------------------
        #  VOL MAX INMEDIATO (,)
        # --------------------------
        if keys[K_COMMA]:
            pygame.mixer.music.set_volume(1.0)
            icono_volumen = sonido_act

    # ==================================================
    #  DIBUJO
    # ==================================================
    if escena_actual == ESCENA_INICIO:
        ventana.blit(fondos["inicio"], (0, 0))
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            texto = fuente.render("Presiona ENTER", True, (255, 255, 255))
            ventana.blit(texto, (280, 500))

    elif escena_actual == ESCENA_PERFILES:
        ventana.blit(fondos["menu"], (0, 0))

        titulo = fuente.render("Selecciona un perfil", True, (255, 255, 0))
        ventana.blit(titulo, (30, 20))

        perfiles = cargar_perfiles()
        y = 150

        for i, p in enumerate(perfiles):
            pid, nombre, vida, tiempo, *_ = p

            color = (255, 255, 0) if perfil_pointer == i else (255, 255, 255)

            texto = fuente.render(
                f"{pid}. {nombre if nombre else '[VACIO]'} | Tiempo {formatear_tiempo(tiempo)}",
                True,
                color
            )
            ventana.blit(texto, (120, y))

            if perfil_pointer == i:
                pygame.draw.rect(ventana, (255, 255, 0), (110, y - 5, 580, 50), 2)

            y += 80

    elif escena_actual == ESCENA_CREAR_PERFIL:
        ventana.fill((0, 20, 40))
        ventana.blit(fuente.render("Escribe tu nombre:", True, (255, 255, 255)), (260, 200))
        ventana.blit(fuente.render(nombre_temporal, True, (255, 255, 0)), (260, 260))
        ventana.blit(fuente.render("(ENTER para continuar)", True, (200, 200, 200)), (260, 320))


 #cargar mapa
    elif escena_actual == ESCENA_JUEGO:
        ventana.blit(fondos["escena_1"], (0, 0))
        nombre, vida, tiempo, x, y, nivel, clase, icono = cargar_perfil(perfil_seleccionado)[1:]

        panel = fuente.render(f"{nombre} | Vida: {vida} | Nivel: {nivel}", True, (255, 255, 255))
        ventana.blit(panel, (20, 20))

        ahora = time.time()
        if ahora - ultimo_guardado >= 1:
            guardar_tiempo(perfil_seleccionado, 1)
            ultimo_guardado = ahora

    # Ícono de volumen
    if icono_volumen:
        ventana.blit(icono_volumen, (690, 5))

    pygame.display.flip()
    reloj.tick(60)

