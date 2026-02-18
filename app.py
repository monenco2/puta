from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "clave_super_segura_123"

# 🔗 CONEXIÓN A NEON (Render usa DATABASE_URL)
database_url = os.environ.get("DATABASE_URL")

# 👇 esto es importante para que funcione con PostgreSQL de Neon
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 🧱 MODELO DE TABLA
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)

# 👤 ADMIN FIJO
ADMIN_USER = "admin"
ADMIN_PASS = "1234"


# 🌐 HOME (PÚBLICO)
@app.route("/")
def home():
    pages = Page.query.all()
    return render_template("page.html", pages=pages)


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")

        if user == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")

    return render_template("login.html")


# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ⚙️ PANEL ADMIN
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    pages = Page.query.all()
    return render_template("admin.html", pages=pages)


# ➕ CREAR NUEVA PAGINA
@app.route("/crear", methods=["POST"])
def crear():
    if not session.get("admin"):
        return redirect("/login")

    titulo = request.form.get("titulo")
    contenido = request.form.get("contenido")

    nueva = Page(titulo=titulo, contenido=contenido)
    db.session.add(nueva)
    db.session.commit()

    return redirect("/admin")


# ✏️ EDITAR PAGINA
@app.route("/editor/<int:id>", methods=["GET", "POST"])
def editor(id):
    if not session.get("admin"):
        return redirect("/login")

    page = Page.query.get_or_404(id)

    if request.method == "POST":
        page.titulo = request.form.get("titulo")
        page.contenido = request.form.get("contenido")
        db.session.commit()
        return redirect("/admin")

    return render_template("editor.html", page=page)


# 🗑️ ELIMINAR PAGINA (extra)
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if not session.get("admin"):
        return redirect("/login")

    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()

    return redirect("/admin")


# 🔥 CREAR TABLAS AUTOMÁTICAMENTE (SOLUCIONA TU ERROR DE NEON)
with app.app_context():
    db.create_all()


# 🚀 INICIO LOCAL
if __name__ == "__main__":
    app.run(debug=True)
