import pygame, sys, time, os
from pygame.locals import *
# Asegúrate de que 'db' existe o comenta esta línea si no tienes la DB configurada
from db import (
    cargar_perfiles, crear_perfil, borrar_perfil,
    guardar_tiempo, cargar_perfil, cerrar_bd
)

# Asegurar ruta correcta
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.mixer.init()

# --- 1. Definiciones de Sprite y Pantalla ---
FRAME = [0, 70, 140, 210, 280, 350, 420, 490, 560, 630]
NUM_FRAMES = len(FRAME)
NUEVO_SPRITE = 70

# Dimensiones de cuadro personalizadas por dirección en la imagen
FRAME_DIMENSION = {
    "down": (NUEVO_SPRITE, 65),
    "left": (NUEVO_SPRITE, 60),
    "up": (NUEVO_SPRITE, 55),
    "right": (NUEVO_SPRITE, 65)
}

# Creacion de la ventana
VENTANA_ANCHO = 800
VENTANA_LARGO = 600
ventana = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_LARGO))
pygame.display.set_caption("Secretos del Reino Hundido")

# --- Lista para guardar todos los obstáculos (¡TUS COLISIONES!) ---
colision_objetos = []

# --- Paredes y Muebles Principales ---
# Nota: Las coordenadas son relativas a la imagen de fondo (800x600)

# pared superior
colision_objetos.append(pygame.Rect(100, 50, 270, 30))  # izquierdo
colision_objetos.append(pygame.Rect(450, 50, 230, 30))  # derecha

#  Pared Izquierda
colision_objetos.append(pygame.Rect(100, 50, 30, 480))

#  Pared Derecha
colision_objetos.append(pygame.Rect(690, 50, 30, 480))

#  Pared Inferior
colision_objetos.append(pygame.Rect(250, 515, 120, 30))  # izquierda
colision_objetos.append(pygame.Rect(450, 515, 230, 30))  # derecha

# esquinas
colision_objetos.append(pygame.Rect(660, 490, 20, 20))  # inferior derecha
colision_objetos.append(pygame.Rect(665, 75, 20, 20))  # superior derecha

# --- Muebles Específicos (Mesas, Alacenas) ---
# barra
colision_objetos.append(pygame.Rect(300, 160, 210, 40))
colision_objetos.append(pygame.Rect(300, 80, 20, 80))

# vitrinas
colision_objetos.append(pygame.Rect(220, 160, 20, 50))  # izquierda
colision_objetos.append(pygame.Rect(580, 160, 20, 50))

# Mesa de la izquierda
colision_objetos.append(pygame.Rect(230, 280, 60, 80))

# Mesa de la derecha
colision_objetos.append(pygame.Rect(530, 280, 60, 80))

# Planta Grande
colision_objetos.append(pygame.Rect(150, 430, 100, 90))

# Fuentes
fuente = pygame.font.Font(None, 36)
fuente1 = pygame.font.SysFont("DejaVu Sans", 20)

# --- Carga y Recorte de la Hoja de Sprites ---
try:
    hoja_sprite = pygame.image.load('imagenes/perfil1.png')
except pygame.error as e:
    print(f"Error al cargar la imagen: perfil1.png. {e}")
    pygame.quit()
    sys.exit()

# ------------------------------
#   FONDOS
# ------------------------------
try:
    fondos = {
        "inicio": pygame.image.load("imagenes/inicio.png"),
        "menu": pygame.image.load("imagenes/menu.png"),
        "escena_1": pygame.image.load("imagenes/escena_1.png")
    }
except pygame.error as e:
    print(f"Error al cargar fondos: {e}")
    pygame.quit()
    sys.exit()


# ------------------------------
#   FUNCIONES DE SPRITE/ANIMACIÓN
# ------------------------------
def recortar_sprite(sheet, x, y, width, height, scale_factor=1):
    """Recorta un sprite."""
    imagen = pygame.Surface([width, height], pygame.SRCALPHA)
    imagen.blit(sheet, (0, 0), (x, y, width, height))
    if scale_factor != 1:
        imagen = pygame.transform.scale(imagen, (width * scale_factor, height * scale_factor))
    return imagen


animacion_frames = {
    "down": [], "left": [], "right": [], "up": []
}

desplazamiento_y_actual = 0

# Carga y recorta todos los frames
for direction in ["down", "left", "up", "right"]:
    width, height = FRAME_DIMENSION[direction]
    y_pos = desplazamiento_y_actual
    for x_pos in FRAME:
        frame = recortar_sprite(hoja_sprite, x_pos, y_pos, width, height)
        animacion_frames[direction].append(frame)
    desplazamiento_y_actual += height

# --- Clase Player (Lógica con Colisiones) ---

class Jugador(pygame.sprite.Sprite):
    def __init__(self, frames, x=VENTANA_ANCHO // 2, y=VENTANA_LARGO // 2):
        super().__init__()
        self.frames = frames

        self.direction = "down"
        self.frame_index = 0
        self.animation_speed = 0.15

        self.image = self.frames[self.direction][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4
        self.vel_x = 0
        self.vel_y = 0

    def actualizar(self):
        # 1. Animación (Mantenida)
        if self.vel_x != 0 or self.vel_y != 0:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames[self.direction]):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = self.frames[self.direction][int(self.frame_index)]

        # Nota: El movimiento real se manejará en 'move_and_collide' en el bucle principal.
        # Aquí solo se actualiza la animación, no la posición.

    def mover_y_colision(self, collision_list):
        # Mover en X y verificar colisión
        self.rect.x += self.vel_x
        # 2. Verificar Colisión en X y revertir si es necesario
        for obstacle_rect in collision_list:
            if self.rect.colliderect(obstacle_rect):
                if self.vel_x > 0:  # Moviéndose a la derecha
                    self.rect.right = obstacle_rect.left
                elif self.vel_x < 0:  # Moviéndose a la izquierda
                    self.rect.left = obstacle_rect.right
                # Importante: Detener el movimiento en el eje para evitar que se aplique
                # en el siguiente frame hasta que el usuario se mueva en otra dirección.
                self.vel_x = 0
                break

        # Mover en Y y verificar colisión
        self.rect.y += self.vel_y
        # 3. Verificar Colisión en Y y revertir si es necesario
        for obstacle_rect in collision_list:
            if self.rect.colliderect(obstacle_rect):
                if self.vel_y > 0:  # Moviéndose hacia abajo
                    self.rect.bottom = obstacle_rect.top
                elif self.vel_y < 0:  # Moviéndose hacia arriba
                    self.rect.top = obstacle_rect.bottom
                self.vel_y = 0
                break

        # 4. Asegurar que el jugador no salga de los límites de la ventana
        self.rect.clamp_ip(ventana.get_rect())


# ------------------------------
#   VARIABLES GLOBALES DEL JUEGO
# ------------------------------
ESCENA_INICIO = 0
ESCENA_PERFILES = 1
ESCENA_CREAR_PERFIL = 2
ESCENA_JUEGO = 3
ESCENA_MENU = 4

escena_actual = ESCENA_INICIO
perfil_pointer = 0
perfil_seleccionado = None

reloj = pygame.time.Clock()
ultimo_guardado = time.time()

# ------------------------------
#   INSTANCIA DEL JUGADOR Y GRUPO
# ------------------------------
jugador = Jugador(animacion_frames)
all_sprites = pygame.sprite.Group(jugador)

# ------------------------------
#   MUSICA Y SONIDOS
# ------------------------------
pygame.mixer.music.load("sonido/Jeremy_Korpas.ogg")
pygame.mixer.music.play(-1)

enter = pygame.mixer.Sound("sonido/enter.ogg")

# Control de música por escena
musica_actual = "menu"

# Iconos de volumen
try:
    sonido_arriba = pygame.image.load('sonido/sonido_arriba.png')
    sonido_abajo = pygame.image.load('sonido/sonido_abajo.png')
    sonido_mute = pygame.image.load('sonido/sonido_mute.png')
    sonido_max = pygame.image.load('sonido/sonido_max.png')
    sonido_act = pygame.image.load('sonido/sonido_act.png')
except pygame.error as e:
    print(f"Error al cargar iconos de volumen: {e}. Usando valores por defecto.")


    # Crear superficies de texto o color simple como fallback
    def create_fallback_icon(text, color):
        s = pygame.Surface((30, 30))
        s.fill(color)
        t = fuente.render(text, True, (255, 255, 255))
        s.blit(t, (5, 5))
        return s


    sonido_arriba = create_fallback_icon('+', (0, 100, 0))
    sonido_abajo = create_fallback_icon('-', (100, 0, 0))
    sonido_mute = create_fallback_icon('X', (50, 50, 50))
    sonido_max = create_fallback_icon('++', (0, 150, 0))
    sonido_act = create_fallback_icon('O', (0, 0, 150))

icono_volumen = None
ultimo_cambio_volumen = 0

# ------------------------------
#   VARIABLES DE ESTADO
# ------------------------------
nombre_temporal = ""
menu_pausa_activo = False
opcion_menu = 0
opciones_menu = ["Continuar", "Guardar partida", "Salir al menú"]
mensaje_guardado = ""
tiempo_mensaje = 0


# ------------------------------
#   FORMATEAR TIEMPO
# ------------------------------
def formatear_tiempo(segundos):
    segundos = int(segundos)
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    return f"{horas:02d}h {minutos:02d}m"


# ------------------------------
#   FADE-IN SUAVE Y TRANSICIÓN
# ------------------------------
def fade_in_musica(vol_final=0.7, duracion=1500):
    pasos = 30
    retraso = max(1, duracion // pasos)
    for i in range(pasos):
        vol = (i / pasos) * vol_final
        pygame.mixer.music.set_volume(vol)
        pygame.time.delay(retraso)


def transicion(ventana, duracion=700):
    """
    IMPORTANTE: Esta función BLOQUEA el bucle principal mientras se ejecuta.
    Si el juego se siente congelado, esta es la causa.
    """
    ancho, alto = ventana.get_size()
    centro = (ancho // 2, alto // 2)
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    # El fadeout de la música puede ser lento, se ejecuta en paralelo,
    # pero el delay general de la función bloquea el programa.
    pygame.mixer.music.fadeout(duracion)

    # Transición de salida (Bloquea)
    for radio in range(max(ancho, alto), 0, -40):
        overlay.fill((0, 0, 0, 255))
        pygame.draw.circle(overlay, (0, 0, 0, 0), centro, radio)
        ventana.blit(overlay, (0, 0))
        pygame.display.update()
        pygame.time.delay(duracion // 30)

    # Pausa corta
    overlay.fill((0, 0, 0))
    ventana.blit(overlay, (0, 0))
    pygame.display.update()
    pygame.time.delay(100)

    # Transición de entrada (Bloquea)
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
    # --- EVENTOS (solo una vez por frame)
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
                    enter.play()
                    escena_actual = ESCENA_PERFILES

            # ------------------------------
            #  ESCENA PERFILES (Carga)
            # ------------------------------
            elif escena_actual == ESCENA_PERFILES:
                perfiles_temp = cargar_perfiles()
                max_index = max(0, len(perfiles_temp) - 1)

                if evento.key == K_UP:
                    perfil_pointer = max(0, perfil_pointer - 1)
                elif evento.key == K_DOWN:
                    perfil_pointer = min(max_index, perfil_pointer + 1)
                elif evento.key == K_RETURN:
                    enter.play()
                    perfiles = perfiles_temp
                    pid, nombre, *_ = perfiles[perfil_pointer]
                    perfil_seleccionado = pid

                    if nombre is None:
                        nombre_temporal = ""
                        escena_actual = ESCENA_CREAR_PERFIL
                    else:
                        # --- Carga de perfil existente (puede ser lento) ---
                        # NOTIFICACIÓN VISUAL para evitar la sensación de congelación
                        ventana.fill((0, 0, 0))
                        texto_cargando = fuente.render("C A R G A N D O . . .", True, (255, 215, 0))
                        ventana.blit(texto_cargando, (VENTANA_ANCHO // 5 - texto_cargando.get_width() // 2,
                                                      VENTANA_LARGO // 1.1 - texto_cargando.get_height() // 2))
                        pygame.display.flip()

                        transicion(ventana)
                        musica_actual = "menu"
                        escena_actual = ESCENA_JUEGO
                        # Cargar posición inicial del jugador (si la db la tiene)
                        try:
                            # Esta llamada a la DB puede ser la que cause un pequeño lag al inicio del juego
                            _, _, _, x, y, _, _, _ = cargar_perfil(perfil_seleccionado)
                            jugador.rect.topleft = (x, y)
                        except:
                            # Posición inicial por defecto si falla la carga
                            jugador.rect.topleft = (VENTANA_ANCHO // 2, VENTANA_LARGO // 2)

                    ultimo_guardado = time.time()
                elif evento.key == K_b:
                    perfiles = cargar_perfiles()
                    pid, _, *_ = perfiles[perfil_pointer]
                    borrar_perfil(pid)

            # ------------------------------
            #  MENÚ DEL JUEGO
            # ------------------------------
            elif escena_actual == ESCENA_JUEGO:
                if evento.key == K_ESCAPE:
                    menu_pausa_activo = not menu_pausa_activo
                    opcion_menu = 0

                if menu_pausa_activo:
                    if evento.key == K_UP:
                        opcion_menu = (opcion_menu - 1) % len(opciones_menu)
                    elif evento.key == K_DOWN:
                        opcion_menu = (opcion_menu + 1) % len(opciones_menu)
                    elif evento.key == K_RETURN:
                        seleccion = opciones_menu[opcion_menu]
                        if seleccion == "Continuar":
                            menu_pausa_activo = False
                        elif seleccion == "Guardar partida":
                            # Guardar posición actual del jugador
                            guardar_tiempo(perfil_seleccionado, 0, x=jugador.rect.x, y=jugador.rect.y)
                            mensaje_guardado = "¡Partida guardada!"
                            tiempo_mensaje = time.time()
                        elif seleccion == "Salir al menú":
                            transicion(ventana)
                            escena_actual = ESCENA_INICIO
                            menu_pausa_activo = False

            # ------------------------------
            #  CREAR PERFIL (Aquí estaba el "freeze")
            # ------------------------------
            elif escena_actual == ESCENA_CREAR_PERFIL:
                if evento.key == K_ESCAPE:
                    nombre_temporal = ""
                    escena_actual = ESCENA_PERFILES
                elif evento.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                    pass
                elif evento.key == K_RETURN:
                    if nombre_temporal.strip() != "":
                        enter.play()

                        # --- Punto clave: Notificación antes de I/O y BLOQUEO ---
                        ventana.fill((0, 20, 40))
                        ventana.blit(fondos["menu"], (0, 0))
                        texto_guardando = fuente.render("G U A R D A N D O . . .", True, (255, 255, 0))
                        ventana.blit(texto_guardando, (VENTANA_ANCHO // 2 - texto_guardando.get_width() // 2,
                                                       VENTANA_LARGO // 2 - texto_guardando.get_height() // 2))
                        pygame.display.flip()

                        # Operación de base de datos (crear perfil)
                        crear_perfil(
                            perfil_seleccionado,
                            nombre_temporal,
                            "Unico",
                            jugador.rect.x,  # Posición X inicial
                            jugador.rect.y  # Posición Y inicial
                        )

                        # Transición (Bloquea el bucle por ~1.5 segundos)
                        transicion(ventana)

                        musica_actual = "menu"
                        escena_actual = ESCENA_JUEGO
                        ultimo_guardado = time.time()
                        nombre_temporal = ""
                elif evento.key == K_BACKSPACE:
                    nombre_temporal = nombre_temporal[:-1]
                else:
                    if evento.unicode and evento.unicode.isprintable() and len(nombre_temporal) < 15:
                        nombre_temporal += evento.unicode

    # ==================================================
    #  CONTROL DE MOVIMIENTO DEL JUGADOR
    # ==================================================
    teclas = pygame.key.get_pressed()

    if escena_actual == ESCENA_JUEGO and not menu_pausa_activo:
        # 1. Resetear velocidad para el frame actual
        jugador.vel_x = 0
        jugador.vel_y = 0

        # 2. Capturar entrada y determinar dirección/velocidad
        if teclas[pygame.K_LEFT]:
            jugador.vel_x = -jugador.speed
            jugador.direction = "left"
        if teclas[pygame.K_RIGHT]:
            jugador.vel_x = jugador.speed
            jugador.direction = "right"
        if teclas[pygame.K_UP]:
            jugador.vel_y = -jugador.speed
            jugador.direction = "up"
        if teclas[pygame.K_DOWN]:
            jugador.vel_y = jugador.speed
            jugador.direction = "down"

        # 3. Mover y verificar colisiones
        # Aquí es donde se aplica la nueva lógica de colisiones
        jugador.mover_y_colision(colision_objetos)

        # 4. Actualiza la animación (basada en si se movió o no)
        jugador.actualizar()

    # ------------------------------
    #  CONTROL DE VOLUMEN (Fuera del movimiento)
    # ------------------------------
    # He corregido la indentación de esta sección.
    if escena_actual != ESCENA_CREAR_PERFIL:
        # BAJAR VOL (9)
        if teclas[K_9]:
            vol = pygame.mixer.music.get_volume()
            vol = max(0.0, vol - 0.01)
            pygame.mixer.music.set_volume(vol)
            icono_volumen = sonido_mute if vol == 0.0 else sonido_abajo
            ultimo_cambio_volumen = time.time()
        # SUBIR VOL (0)
        if teclas[K_0]:
            vol = pygame.mixer.music.get_volume()
            vol = min(1.0, vol + 0.01)
            pygame.mixer.music.set_volume(vol)
            icono_volumen = sonido_max if vol == 1.0 else sonido_arriba
            ultimo_cambio_volumen = time.time()
        # MUTE (M)
        if teclas[K_m]:
            pygame.mixer.music.set_volume(0.0)
            icono_volumen = sonido_mute
            ultimo_cambio_volumen = time.time()
        # ACTIVAR SOLO SI ESTÁ EN MUTE (,)
        if teclas[K_COMMA]:
            vol = pygame.mixer.music.get_volume()
            if vol == 0.0:
                pygame.mixer.music.set_volume(0.4)
                icono_volumen = sonido_act
                ultimo_cambio_volumen = time.time()

    # ==================================================
    #   DIBUJO POR ESCENA
    # ==================================================
    if escena_actual == ESCENA_INICIO:
        ventana.blit(fondos["inicio"], (0, 0))
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            texto = fuente.render("Presiona ENTER", True, (255, 255, 255))
            ventana.blit(texto, (280, 500))

    elif escena_actual == ESCENA_PERFILES:
        ventana.blit(fondos["menu"], (0, 0))
        ventana.blit(fuente.render("Selecciona un perfil", True, (255, 255, 0)), (30, 20))
        ventana.blit(
            fuente1.render(" ↑ ↓ :Moverse | B : Borrar perfil | Enter: Seleccionar perfil", True, (255, 255, 255)),
            (30, 550))
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
        ventana.blit(fondos["menu"], (0, 0))
        ventana.blit(fuente.render("Escribe tu nombre:", True, (255, 255, 255)), (260, 200))
        # Cursor parpadeante
        cursor = ""
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor = "_"

        texto_nombre = fuente.render(nombre_temporal + cursor, True, (255, 255, 0))
        ventana.blit(texto_nombre, (260, 260))
        ventana.blit(fuente1.render("Enter : Continuar | Esc: Regresar al menu", True, (255, 255, 255)), (30, 550))

    elif escena_actual == ESCENA_JUEGO:
        ventana.blit(fondos["escena_1"], (0, 0))

        # --- DIBUJAR RECTÁNGULOS DE COLISIÓN (PARA DEPURACIÓN) ---
        # EL SIGUIENTE BLOQUE DE CÓDIGO HA SIDO COMENTADO PARA OCULTAR
        # LOS RECTÁNGULOS ROJOS DE COLISIÓN.
        # --- DIBUJAR RECTÁNGULOS DE COLISIÓN (PARA DEPURACIÓN) ---
        #color_colision = (255, 0, 0)  # Rojo
        #grosor_linea = 2  # Dibuja solo el borde para que sea menos invasivo
        #for rect in collision_objects:
        #    pygame.draw.rect(ventana, color_colision, rect, grosor_linea)
        # --------------------------------------------------------


        # CAMBIO DE MÚSICA
        if musica_actual != "juego":
            pygame.mixer.music.load("sonido/Village_Rynoka.ogg")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.0)
            fade_in_musica(0.7, 1500)
            musica_actual = "juego"

        # Cargar datos del perfil
        try:
            nombre, vida, tiempo, x, y, Dinero, clase, icono = cargar_perfil(perfil_seleccionado)[1:]
        except Exception:
            nombre, vida, tiempo, x, y, Dinero, clase = ("", 100, 0, 0, 0, 0, "Unico")

        panel = fuente.render(f"{nombre} | Vida: {vida} | $: {Dinero}", True, (255, 255, 255))
        ventana.blit(panel, (20, 20))

        # DIBUJAR AL JUGADOR
        all_sprites.draw(ventana)

        # --- Guardado automático de tiempo y posición ---
        ahora = time.time()
        if ahora - ultimo_guardado >= 1:
            guardar_tiempo(perfil_seleccionado, 1, x=jugador.rect.x, y=jugador.rect.y)
            ultimo_guardado = ahora

        # --- MENÚ DE PAUSA
        if menu_pausa_activo:
            overlay = pygame.Surface(ventana.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            ventana.blit(overlay, (0, 0))

            # Dibujar opciones
            y_inicio = 200
            for i, opcion in enumerate(opciones_menu):
                color = (255, 255, 0) if i == opcion_menu else (255, 255, 255)
                texto = fuente.render(opcion, True, color)
                ventana.blit(texto, (300, y_inicio + i * 50))

        # --- Mostrar mensaje de guardado ---
        if mensaje_guardado and time.time() - tiempo_mensaje < 2:
            texto = fuente.render(mensaje_guardado, True, (0, 255, 0))
            ventana.blit(texto, (530, 530))

    # Ícono de volumen por 2 segundos
    if icono_volumen and (time.time() - ultimo_cambio_volumen < 2):
        ventana.blit(icono_volumen, (690, 5))

    pygame.display.flip()
    reloj.tick(60)

