from flask import Flask, request, jsonify, send_from_directory, session
from database import crear_tablas, conectar, crear_usuario
from werkzeug.security import check_password_hash
import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory, session, redirect

app = Flask(__name__)

app.secret_key = os.environ.get("FORVEX_SECRET_KEY", "cambia-esta-clave-secreta")

crear_tablas()

from database import crear_tabla_torneos
from database import crear_tabla_inscripciones
crear_tabla_inscripciones()

crear_tabla_torneos()

@app.route("/")
def inicio():
    return send_from_directory("../frontend", "index.html")

@app.route("/sala.html")
def pagina_sala():
    carpeta_frontend = os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend"
    )

    return send_from_directory(carpeta_frontend, "sala.html")

@app.route("/sala.css")
def estilos_sala():
    carpeta_frontend = os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend"
    )

    return send_from_directory(carpeta_frontend, "sala.css")

@app.route("/sala.js")
def javascript_sala():
    carpeta_frontend = os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend"
    )

    return send_from_directory(carpeta_frontend, "sala.js")

@app.route("/registro")
def pagina_registro():
    return send_from_directory("../frontend", "registro.html")

@app.route("/login")
def pagina_login():
    return send_from_directory("../frontend", "login.html")


@app.route("/login.css")
def login_css():
    return send_from_directory("../frontend", "login.css")

@app.route("/registro.css")
def registro_css():
    return send_from_directory("../frontend", "registro.css")

@app.route("/estilos.css")
def estilos():
    return send_from_directory("../frontend", "estilos.css")

@app.route("/imagenes/<path:archivo>")
def imagenes(archivo):
    return send_from_directory("../frontend", archivo)

@app.route("/js/<path:archivo>")
def javascript(archivo):
    return send_from_directory("../frontend", archivo)


@app.route("/api/admin/login", methods=["POST"])
def login_admin():
    datos = request.get_json()

    correo = datos.get("correo", "").strip()
    password = datos.get("password", "")

    conexion = conectar()

    admin = conexion.execute(
        "SELECT * FROM administradores WHERE correo = ?",
        (correo,)
    ).fetchone()

    conexion.close()

    if admin and check_password_hash(admin["password_hash"], password):
        session["admin_id"] = admin["id"]
        return jsonify({"mensaje": "Inicio de sesión correcto"})

    return jsonify({"error": "Correo o contraseña incorrectos"}), 401

@app.route("/api/registro", methods=["POST"])
def registro_usuario():

    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400

    nombre = datos.get("nombre", "").strip()
    correo = datos.get("correo", "").strip().lower()
    password = datos.get("password", "")

    if not nombre or not correo or not password:
        return jsonify({"error": "Completa todos los campos"}), 400

    if len(password) < 8:
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres"
        }), 400

    creado = crear_usuario(nombre, correo, password)

    if not creado:
        return jsonify({
            "error": "Este correo ya está registrado"
        }), 409

    return jsonify({
        "mensaje": "Cuenta creada correctamente"
    }), 201

@app.route("/api/login", methods=["POST"])
def login_usuario():

    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400

    correo = datos.get("correo", "").strip().lower()
    password = datos.get("password", "")

    conexion = conectar()

    usuario = conexion.execute("""
        SELECT * FROM usuarios
        WHERE correo = ?
    """, (correo,)).fetchone()

    conexion.close()

    if not usuario or not check_password_hash(usuario["password_hash"], password):
        return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    session["usuario_id"] = usuario["id"]
    session["usuario_nombre"] = usuario["nombre"]

    return jsonify({
        "mensaje": "Inicio de sesión correcto",
        "nombre": usuario["nombre"]
    })

@app.route("/api/me", methods=["GET"])
def obtener_usuario():

    if "usuario_id" not in session:
        return jsonify({
            "autenticado": False
        }), 401

    return jsonify({
        "autenticado": True,
        "id": session["usuario_id"],
        "nombre": session["usuario_nombre"]
    })

@app.route("/api/logout", methods=["POST"])
def logout_usuario():

    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)

    return jsonify({
        "mensaje": "Sesión cerrada correctamente"
    })

@app.route("/api/admin/logout", methods=["POST"])
def logout_admin():
    session.pop("admin_id", None)
    return jsonify({"mensaje": "Sesión administrativa cerrada correctamente"})

@app.route("/api/inscripciones", methods=["POST"])
def inscribir_jugador():

    if "usuario_id" not in session:
        return jsonify({"error": "Debes iniciar sesión para inscribirte"}), 401

    datos = request.get_json()

    if not datos or not datos.get("torneo_id"):
        return jsonify({"error": "No se recibió el torneo"}), 400

    torneo_id = datos["torneo_id"]
    usuario_id = session["usuario_id"]

    conexion = conectar()

    try:
        conexion.execute("BEGIN IMMEDIATE")

        torneo = conexion.execute("""
            SELECT * FROM torneos
            WHERE id = ? AND estado = 'publicado'
        """, (torneo_id,)).fetchone()

        if not torneo:
            return jsonify({"error": "El torneo no existe o no está publicado"}), 404

        inscritos = conexion.execute("""
            SELECT COUNT(*) AS total
            FROM inscripciones
            WHERE torneo_id = ?
        """, (torneo_id,)).fetchone()["total"]

        if inscritos >= torneo["cupos"]:
            return jsonify({"error": "Este torneo ya no tiene cupos disponibles"}), 409

        conexion.execute("""
            INSERT INTO inscripciones (usuario_id, torneo_id)
            VALUES (?, ?)
        """, (usuario_id, torneo_id))

        conexion.commit()

        return jsonify({"mensaje": "¡Te has inscrito correctamente!"}), 201

    except sqlite3.IntegrityError:
        conexion.rollback()
        return jsonify({"error": "Ya estás inscrito en este torneo"}), 409

    finally:
        conexion.close()

@app.route("/api/torneos/<int:torneo_id>/sala", methods=["GET"])
def obtener_sala(torneo_id):

    if "usuario_id" not in session:
        return jsonify({"error": "Debes iniciar sesión"}), 401

    usuario_id = session["usuario_id"]

    conexion = conectar()

    inscripcion = conexion.execute("""
        SELECT id
        FROM inscripciones
        WHERE usuario_id = ? AND torneo_id = ?
    """, (usuario_id, torneo_id)).fetchone()

    if not inscripcion:
        conexion.close()
        return jsonify({"error": "No tienes acceso a esta sala"}), 403

    torneo = conexion.execute("""
        SELECT sala_id, sala_password
        FROM torneos
        WHERE id = ?
    """, (torneo_id,)).fetchone()

    conexion.close()

    if not torneo:
        return jsonify({"error": "Torneo no encontrado"}), 404

    return jsonify({
        "sala_id": torneo["sala_id"],
        "sala_password": torneo["sala_password"]
    })

@app.route("/api/torneos/<int:torneo_id>/mi-inscripcion", methods=["GET"])
def comprobar_inscripcion(torneo_id):

    if "usuario_id" not in session:
        return jsonify({"inscrito": False})

    conexion = conectar()

    inscripcion = conexion.execute("""
        SELECT id
        FROM inscripciones
        WHERE usuario_id = ? AND torneo_id = ?
    """, (session["usuario_id"], torneo_id)).fetchone()

    conexion.close()

    return jsonify({
        "inscrito": inscripcion is not None
    })

@app.route("/admin/login")
def pagina_login_admin():
    if "admin_id" in session:
        return redirect("/admin")

    return send_from_directory("../frontend", "admin-login.html")

@app.route("/admin")
def panel_admin():
    if "admin_id" not in session:
        return redirect("/admin/login")

    return send_from_directory("../frontend", "admin.html")


@app.route("/admin.css")
def admin_css():
    return send_from_directory("../frontend", "admin.css")

@app.route("/api/admin/torneos", methods=["POST"])
def crear_torneo():

    if "admin_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    datos = request.get_json()

    nombre = datos.get("nombre")
    juego = datos.get("juego")
    cupos = datos.get("cupos")
    premios = datos.get("premios")
    fecha = datos.get("fecha")
    reglas = datos.get("reglas", "")
    sala_id = datos.get("sala_id", "").strip()
    sala_password = datos.get("sala_password", "").strip()

    if not all([nombre, juego, premios, fecha, cupos]):
        return jsonify({"error": "Completa todos los campos obligatorios"}), 400

    try:
        cupos = int(cupos)
        if cupos < 1:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Los cupos deben ser un número mayor a cero"}), 400

    conexion = conectar()

    conexion.execute("""
        INSERT INTO torneos
        (nombre, juego, cupos, premios, fecha, reglas, sala_id, sala_password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre, juego, cupos, premios, fecha, reglas,
        sala_id, sala_password
    ))

    conexion.commit()
    conexion.close()

    return jsonify({"mensaje": "Torneo creado correctamente"}), 201

@app.route("/api/admin/torneos", methods=["GET"])
def listar_torneos():

    if "admin_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    conexion = conectar()

    torneos = conexion.execute(
        "SELECT * FROM torneos ORDER BY id DESC"
    ).fetchall()

    conexion.close()

    return jsonify([dict(torneo) for torneo in torneos])

@app.route("/api/torneos/publicados", methods=["GET"])
def torneos_publicados():
    conexion = conectar()

    torneos = conexion.execute("""
        SELECT id, nombre, juego, cupos, premios, fecha, reglas
        FROM torneos
        WHERE estado = 'publicado'
        ORDER BY id DESC
    """).fetchall()

    conexion.close()

    return jsonify([dict(torneo) for torneo in torneos])

@app.route("/api/admin/torneos/<int:id>/publicar", methods=["POST"])
def publicar_torneo(id):
    if "admin_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    conexion = conectar()

    resultado = conexion.execute("""
        UPDATE torneos
        SET estado = 'publicado'
        WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    if resultado.rowcount == 0:
        return jsonify({"error": "Torneo no encontrado"}), 404

    return jsonify({"mensaje": "Torneo publicado correctamente"})

@app.route("/api/admin/torneos/<int:id>/eliminar", methods=["DELETE"])
def eliminar_torneo(id):

    if "admin_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    conexion = conectar()

    conexion.execute("""
        DELETE FROM inscripciones
        WHERE torneo_id = ?
    """, (id,))

    resultado = conexion.execute("""
        DELETE FROM torneos
        WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    if resultado.rowcount == 0:
        return jsonify({"error": "Torneo no encontrado"}), 404

    return jsonify({"mensaje": "Torneo eliminado correctamente"})

if __name__ == "__main__":
    app.run(debug=True)
