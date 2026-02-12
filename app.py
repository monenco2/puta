from flask import Flask, render_template, request, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-super-secreta"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

PAGES_FILE = "pages.json"


# -------------------
# FUNCIONES
# -------------------
def load_pages():
    if not os.path.exists(PAGES_FILE):
        return {}
    with open(PAGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_pages(data):
    with open(PAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------
# LOGIN
# -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        if user == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -------------------
# PANEL ADMIN
# -------------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    pages = load_pages()
    return render_template("admin.html", pages=pages)


# -------------------
# EDITOR
# -------------------
@app.route("/editor/<page_name>", methods=["GET", "POST"])
def editor(page_name):
    if not session.get("admin"):
        return redirect("/login")

    pages = load_pages()

    if request.method == "POST":
        pages[page_name] = {
            "titulo": request.form["titulo"],
            "contenido": request.form["contenido"]
        }
        save_pages(pages)
        return redirect("/admin")

    page = pages.get(page_name, {"titulo": "", "contenido": ""})
    return render_template("editor.html", page=page, page_name=page_name)


# -------------------
# PÁGINAS PÚBLICAS
# -------------------
@app.route("/page/<page_name>")
def show_page(page_name):
    pages = load_pages()
    page = pages.get(page_name)

    if not page:
        return "<h1>Página no encontrada</h1>"

    return render_template("page.html", page=page)


if __name__ == "__main__":
    app.run(debug=True)
