from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# 🔐 clave secreta
app.secret_key = "clave_super_segura"

# 🗄️ conexión a NEON (Render usa DATABASE_URL)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 🧱 MODELO DE PAGINAS
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    contenido = db.Column(db.Text)

# 👤 usuario fijo (admin)
USER = "admin"
PASS = "1234"


# 🌐 HOME
@app.route("/")
def home():
    pages = Page.query.all()
    return render_template("page.html", pages=pages)


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user == USER and password == PASS:
            session["user"] = user
            return redirect("/admin")
    return render_template("login.html")


# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ⚙️ ADMIN PANEL
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")

    pages = Page.query.all()
    return render_template("admin.html", pages=pages)


# ✏️ EDITOR
@app.route("/editor/<int:id>", methods=["GET", "POST"])
def editor(id):
    if "user" not in session:
        return redirect("/login")

    page = Page.query.get(id)

    if request.method == "POST":
        page.titulo = request.form["titulo"]
        page.contenido = request.form["contenido"]
        db.session.commit()
        return redirect("/admin")

    return render_template("editor.html", page=page)


# ➕ CREAR NUEVA PAGINA
@app.route("/crear", methods=["POST"])
def crear():
    if "user" not in session:
        return redirect("/login")

    titulo = request.form["titulo"]
    contenido = request.form["contenido"]

    nueva = Page(titulo=titulo, contenido=contenido)
    db.session.add(nueva)
    db.session.commit()

    return redirect("/admin")


# 🚀 iniciar
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
