# ============================================
# IMPORTS
# ============================================

import os
import secrets

from flask import Flask, request, jsonify, render_template, session, redirect, url_for

import mysql.connector


# ============================================
# APPLICATION SETUP
# ============================================

# create the Flask instance
app = Flask(__name__)

# secret key used to sign sessions (cookies)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)


# ============================================
# DATABASE CONNECTION (MySQL/MariaDB)
# ============================================

# database configuration
DB_CONFIG = {
    "host": "localhost",  # database server
    "port": 3308,  # native MariaDB port
    # 3306 is used by LAMPP, 3307 by the docker container
    "user": "labuser",  # user
    "password": "labpass",  # password
    "database": "login_app",  # database name
}


# function that creates a fresh connection per request
# avoids the error: "Unread result found"
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ============================================
# MAIN ROUTES
# ============================================


# main route -> loads the login page
@app.route("/")
def home():
    return render_template("index.html")


# ============================================
# PROTECTED ROUTES (require session)
# ============================================


@app.route("/blog")
def blog():
    # check if the user is logged in
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    return render_template("blog.html")


@app.route("/about")
def about():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    return render_template("about.html")


# ============================================
# CONTACT (VULNERABLE XSS)
# ============================================


@app.route("/contact", methods=["GET", "POST"])
def contact():
    # check session
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    # variables that will be sent to the HTML
    name = ""
    reason = ""
    message = ""

    # if the user submits the form
    if request.method == "POST":

        # get data from the form
        name = request.form.get("name")
        reason = request.form.get("reason")
        message = request.form.get("message")

        # XSS VULNERABILITY:
        # the message is sent directly to the template
        # and in the HTML it uses |safe -> executes JS
        return render_template(
            "contact.html", name=name, reason=reason, message=message
        )

    # if it is a GET request just load the page
    return render_template("contact.html")


# ============================================
# SEARCH (SQL INJECTION)
# ============================================


@app.route("/search")
def search():
    if not session.get("logged_in"):
        return redirect(url_for("home"))

    # parameter received from the URL (?q=...)
    query_param = request.args.get("q", "")

    results = []
    error = None

    # if there is user input
    if query_param:
        try:
            # fresh connection per request
            db = get_db()
            cursor = db.cursor()

            # SQLi VULNERABILITY:
            # direct concatenation of the user input
            query = f"SELECT id, username FROM users WHERE username = '{query_param}'"

            print(query)  # debug

            # run the query
            cursor.execute(query)

            # get the results
            results = cursor.fetchall()

            # close cursor and connection
            cursor.close()
            db.close()

        except Exception as e:
            # shows SQL errors (information disclosure)
            error = str(e)

    return render_template(
        "search.html", resultados=results, error=error, q=query_param
    )


# ============================================
# LOGIN (SQL INJECTION - AUTH BYPASS)
# ============================================


@app.route("/login", methods=["POST"])
def login():

    # get the JSON sent from the frontend (AJAX)
    data = request.get_json(silent=True) or {}

    # extract credentials
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "error", "message": "Incomplete credentials"}), 400

    # fresh connection per request
    db = get_db()
    cursor = db.cursor()

    # SQLi VULNERABILITY:
    # allows bypass with ' OR '1'='1' --
    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )

    # secure version (commented out)
    # query = "SELECT * FROM users WHERE username = %s AND password = %s"
    # cursor.execute(query, (username, password))

    print(query)

    # run the query
    cursor.execute(query)

    # get all results with fetchall() (not fetchone())
    # reason: with the ' OR '1'='1' -- attack the query returns several rows
    # and if unread rows were left behind, cursor.close() raises "Unread result found"
    result = cursor.fetchall()

    # close cursor and connection
    cursor.close()
    db.close()

    # if a valid user exists
    if result:
        session["logged_in"] = True  # create session
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"}), 401


# ============================================
# DASHBOARD (PROTECTED)
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
    # clear the whole session
    session.clear()

    return redirect(url_for("home"))


# ============================================
# ERROR 404
# ============================================


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ============================================
# SERVER START
# ============================================

if __name__ == "__main__":
    app.run(debug=True)
