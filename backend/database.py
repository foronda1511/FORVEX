import sqlite3
from werkzeug.security import generate_password_hash

def conectar():
    conexion = sqlite3.connect("backend/forvex.db")
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    conexion = conectar()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexion.commit()
    conexion.close()


def crear_administrador(correo, password):
    conexion = conectar()

    password_hash = generate_password_hash(password)

    try:
        conexion.execute("""
            INSERT INTO administradores (correo, password_hash)
            VALUES (?, ?)
        """, (correo, password_hash))

        conexion.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conexion.close()

def crear_tabla_torneos():
    conexion = conectar()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS torneos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            juego TEXT NOT NULL,
            cupos INTEGER NOT NULL,
            premios TEXT NOT NULL,
            fecha TEXT NOT NULL,
            reglas TEXT,
            estado TEXT DEFAULT 'borrador',
            sala_id TEXT,
            sala_password TEXT
        )
    """)

    conexion.commit()
    conexion.close()

def crear_usuario(nombre, correo, password):
    conexion = conectar()

    password_hash = generate_password_hash(password)

    try:
        conexion.execute("""
            INSERT INTO usuarios (nombre, correo, password_hash)
            VALUES (?, ?, ?)
        """, (nombre, correo, password_hash))

        conexion.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conexion.close()

def crear_tabla_inscripciones():
    conexion = conectar()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            torneo_id INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'inscrito',
            fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (torneo_id) REFERENCES torneos(id),

            UNIQUE (usuario_id, torneo_id)
        )
    """)

    conexion.commit()
    conexion.close()