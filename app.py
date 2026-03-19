# ============================================
# IMPORTACIONES
# ============================================

# importar Flask y utilidades necesarias
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

# librería para conectar con MySQL / MariaDB
import mysql.connector


# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================

# crear instancia de Flask
app = Flask(__name__)

# clave secreta para firmar sesiones (cookies)
app.secret_key = "orami_ctf_secret"


# ============================================
# CONEXIÓN A LA BASE DE DATOS
# ============================================

# configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",      # servidor de base de datos
    "user": "labuser",        # usuario
    "password": "labpass",    # contraseña
    "database": "login_app",  # nombre de la BD
}


# función que crea una conexión fresca por cada petición
# evita el error: "Unread result found"
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ============================================
# RUTAS PRINCIPALES
# ============================================

# ruta principal → carga el login
@app.route("/")
def home():
    return render_template("index.html")


# ============================================
# RUTAS PROTEGIDAS (requieren sesión)
# ============================================

@app.route("/blog")
def blog():
    # verificar si el usuario está logueado
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    return render_template("blog.html")


@app.route("/acerca")
def acerca():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    return render_template("acerca.html")


# ============================================
# CONTACTO (XSS VULNERABLE)
# ============================================

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    # verificar sesión
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    # variables que se enviarán al HTML
    nombre = ""
    motivo = ""
    mensaje = ""

    # si el usuario envía el formulario
    if request.method == "POST":

        # obtener datos del formulario
        nombre = request.form.get("nombre")
        motivo = request.form.get("motivo")
        mensaje = request.form.get("mensaje")

        # VULNERABILIDAD XSS:
        # el mensaje se envía directamente al template
        # y en el HTML se usa |safe → ejecuta JS
        return render_template(
            "contacto.html",
            nombre=nombre,
            motivo=motivo,
            mensaje=mensaje
        )

    # si es GET solo carga la página
    return render_template("contacto.html")


# ============================================
# BUSCADOR (SQL INJECTION)
# ============================================

@app.route("/buscar")
def buscar():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    # parámetro recibido por URL (?q=...)
    query_param = request.args.get("q", "")

    resultados = []
    error = None

    # si hay input del usuario
    if query_param:
        try:
            # conexión fresca por petición
            db = get_db()
            cursor = db.cursor()

            # VULNERABILIDAD SQLi:
            # concatenación directa del input del usuario
            query = f"SELECT id, username FROM users WHERE username = '{query_param}'"

            print(query)  # debug

            # ejecutar query
            cursor.execute(query)

            # obtener resultados
            resultados = cursor.fetchall()

            # cerrar cursor y conexión
            cursor.close()
            db.close()

        except Exception as e:
            # muestra errores SQL (information disclosure)
            error = str(e)

    return render_template(
        "buscar.html",
        resultados=resultados,
        error=error,
        q=query_param
    )


# ============================================
# LOGIN (SQL INJECTION - AUTH BYPASS)
# ============================================

@app.route("/login", methods=["POST"])
def login():

    # obtener JSON enviado desde el frontend (AJAX)
    data = request.get_json()

    # extraer credenciales
    username = data.get("username")
    password = data.get("password")

    # conexión fresca por petición
    db = get_db()
    cursor = db.cursor()

    # VULNERABILIDAD SQLi:
    # permite bypass con ' OR '1'='1' --
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    # versión segura (comentada)
    # query = "SELECT * FROM users WHERE username = %s AND password = %s"
    # cursor.execute(query, (username, password))

    print(query)

    # ejecutar query
    cursor.execute(query)

    # obtener un resultado
    result = cursor.fetchone()

    # cerrar cursor y conexión
    cursor.close()
    db.close()

    # si existe usuario válido
    if result:
        session["logged_in"] = True  # crear sesión
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"}), 401


# ============================================
# DASHBOARD (PROTEGIDO)
# ============================================

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    return render_template("dashboard.html")


# ============================================
# LOGOUT
# ============================================

@app.route("/logout")
def logout():
    # eliminar toda la sesión
    session.clear()

    return redirect(url_for("home"))


# ============================================
# ERROR 404
# ============================================

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


# ============================================
# EJECUCIÓN DEL SERVIDOR
# ============================================

# modo debug activado (solo para laboratorio)
app.run(debug=True)
