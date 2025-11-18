import sqlite3

# ===========================
#   CONEXIÓN A LA BASE DE DATOS
# ===========================
conexion = sqlite3.connect("profiles.db")
cursor = conexion.cursor()

# ===========================
#         CREACIÓN BD
# ===========================
def inicializar_bd():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS perfiles (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        vida INTEGER DEFAULT 100,
        tiempo_jugado INTEGER DEFAULT 0,
        pos_x INTEGER DEFAULT 100,
        pos_y INTEGER DEFAULT 100,
        nivel INTEGER DEFAULT 1,
        clase TEXT DEFAULT 'Guerrero',
        icono TEXT DEFAULT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        perfil_id INTEGER,
        objeto TEXT,
        cantidad INTEGER,
        FOREIGN KEY(perfil_id) REFERENCES perfiles(id)
    )
    """)

    # Perfiles vacíos
    cursor.execute("INSERT OR IGNORE INTO perfiles (id, nombre) VALUES (1, NULL)")
    cursor.execute("INSERT OR IGNORE INTO perfiles (id, nombre) VALUES (2, NULL)")

    conexion.commit()

# ===========================
#         FUNCIONES BD
# ===========================
def cargar_perfiles():
    cursor.execute("SELECT * FROM perfiles")
    return cursor.fetchall()

def crear_perfil(id, nombre, clase, icono):
    cursor.execute("""
        UPDATE perfiles 
        SET nombre=?, clase=?, icono=?, vida=100, tiempo_jugado=0, pos_x=100, pos_y=100, nivel=1
        WHERE id=?
    """, (nombre, clase, icono, id))
    conexion.commit()

def borrar_perfil(id):
    cursor.execute("UPDATE perfiles SET nombre=NULL, vida=100, tiempo_jugado=0, pos_x=100, pos_y=100, nivel=1, icono=NULL WHERE id=?", (id,))
    cursor.execute("DELETE FROM inventario WHERE perfil_id=?", (id,))
    conexion.commit()

def guardar_tiempo(id, segundos):
    cursor.execute("UPDATE perfiles SET tiempo_jugado = tiempo_jugado + ? WHERE id=?", (segundos, id))
    conexion.commit()

def cargar_perfil(id):
    cursor.execute("SELECT * FROM perfiles WHERE id=?", (id,))
    return cursor.fetchone()

def cerrar_bd():
    conexion.close()
