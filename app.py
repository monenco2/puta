import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret123")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------- MODELO --------
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    titulo = db.Column(db.String(200))
    contenido = db.Column(db.Text)

# -------- CREAR PAGINAS POR DEFECTO --------
def crear_paginas():
    if not Page.query.filter_by(name="inicio").first():
        db.session.add(Page(name="inicio", titulo="Bienvenido", contenido="Esta es la página principal"))

    if not Page.query.filter_by(name="sobre").first():
        db.session.add(Page(name="sobre", titulo="Sobre Nosotros", contenido="Información sobre nosotros"))

    if not Page.query.filter_by(name="contacto").first():
        db.session.add(Page(name="contacto", titulo="Contacto", contenido="Aquí puedes contactarnos"))

    db.session.commit()

# -------- LOGIN --------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------- ADMIN --------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    pages = Page.query.all()
    return render_template("admin.html", pages=pages)

# -------- EDITOR --------
@app.route("/editor/<name>", methods=["GET","POST"])
def editor(name):
    if not session.get("admin"):
        return redirect("/login")

    page = Page.query.filter_by(name=name).first()

    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]

        if page:
            page.titulo = titulo
            page.contenido = contenido
        else:
            page = Page(name=name, titulo=titulo, contenido=contenido)
            db.session.add(page)

        db.session.commit()
        return redirect("/admin")

    return render_template("editor.html", page=page, name=name)

# -------- MOSTRAR PAGINA --------
@app.route("/<name>")
def page(name):
    page = Page.query.filter_by(name=name).first()
    if not page:
        return "Página no encontrada"
    return render_template("page.html", page=page)

# -------- HOME --------
@app.route("/")
def home():
    return redirect("/inicio")

# -------- INIT --------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        crear_paginas()
    app.run(debug=True)
