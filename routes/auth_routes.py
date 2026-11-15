from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify,
)
from models.user_model import UserModel

auth_bp = Blueprint("auth", __name__)
user_model = UserModel()


# ------------------------------------------------------------
# GET / → renderiza index.html (login + cadastro)
# ------------------------------------------------------------
@auth_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ------------------------------------------------------------
# POST /login
# ------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    cpf = request.form.get("cpf", "").strip()
    senha = request.form.get("password", "")

    user = user_model.autenticar_por_cpf(cpf, senha)

    if user is None:
        flash("CPF ou senha inválidos.", "erro")
        return redirect(url_for("auth.index"))

    session.permanent = True
    session["user_id"] = user.id
    session["user_nome"] = user.nome

    return redirect(url_for("dashboard.dashboard"))

# ------------------------------------------------------------
# GET /logout
# ------------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.index"))

# ------------------------------------------------------------
# POST /cadastro (cadastro de usuário do sistema — index.html)
# ------------------------------------------------------------
@auth_bp.route("/cadastro", methods=["POST"])
def cadastro():
    nome = request.form.get("name_cad", "").strip()
    username = request.form.get("user_cad", "").strip()
    cpf = request.form.get("cpf_cad", "").strip()
    senha = request.form.get("pass_cad", "")

    novo_id = user_model.cadastrar(nome, username, cpf, senha)

    if novo_id is None:
        flash("CPF ou nome de usuário já cadastrado.", "erro")
        return redirect(url_for("auth.index"))

    flash("Cadastro realizado! Faça login.", "sucesso")
    return redirect(url_for("auth.index"))

@auth_bp.route("/api/usuario_logado")
def usuario_logado():
    if "user_id" not in session:
        return jsonify({"erro": "não autenticado"}), 401
    return jsonify({"id": session["user_id"], "nome": session.get("user_nome", "Usuário")})