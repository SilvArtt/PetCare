from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash,
)
from models.pet_model import (
    PetModel, Pet,
    PetError, TutorObrigatorioError, PetComAgendamentosError,
)
from models.tutor_model import TutorModel

pet_bp = Blueprint("pet", __name__)
pet_model = PetModel()
tutor_model = TutorModel()


def _login_obrigatorio():
    return "user_id" not in session


# ------------------------------------------------------------
# GET /pets
# ------------------------------------------------------------
@pet_bp.route("/pets")
def listar_pets():
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    return render_template("pages/p.html")


# ------------------------------------------------------------
# POST /cadastro_pet (ação do formulário p.html)
# ------------------------------------------------------------
@pet_bp.route("/cadastro_pet", methods=["POST"])
def cadastrar_pet():
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    try:
        peso_str = request.form.get("peso", "").replace(",", ".").strip()
        peso = float(peso_str) if peso_str else None

        pet = Pet(
            id=None,
            nome=request.form.get("nome", "").strip(),
            especie=request.form.get("especie", ""),
            raca=request.form.get("raca", ""),
            porte=request.form.get("porte", ""),
            data_nascimento=request.form.get("data_nascimento", ""),
            peso=peso,
            observacoes=request.form.get("observacoes", ""),
            tutor_id=int(request.form["tutor_id"]) if request.form.get("tutor_id") else 0,
        )

        pet_model.cadastrar(pet)
        flash("Pet cadastrado com sucesso!", "sucesso")
    except TutorObrigatorioError as e:
        flash(str(e), "erro")
    except PetError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro inesperado: {e}", "erro")

    return redirect(url_for("pet.listar_pets"))


# ------------------------------------------------------------
# POST /pets/<id>/excluir
# ------------------------------------------------------------
@pet_bp.route("/pets/<int:pet_id>/excluir", methods=["POST"])
def excluir_pet(pet_id):
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    try:
        pet_model.deletar(pet_id)
        flash("Pet removido.", "sucesso")
    except PetComAgendamentosError as e:
        flash(str(e), "erro")

    return redirect(url_for("pet.listar_pets"))


# ------------------------------------------------------------
# GET /api/pets (para JS — com nome do tutor)
# ------------------------------------------------------------
@pet_bp.route("/api/pets")
def api_listar_pets():
    if _login_obrigatorio():
        return jsonify({"erro": "não autenticado"}), 401

    # listar_todos() já retorna dicts com tutor_nome incluso
    pets = pet_model.listar_todos()
    return jsonify(pets)


# ------------------------------------------------------------
# GET /api/pets_por_tutor/<id> (dropdown de Agendamento)
# ------------------------------------------------------------
@pet_bp.route("/api/pets_por_tutor/<int:tutor_id>")
def api_pets_por_tutor(tutor_id):
    if _login_obrigatorio():
        return jsonify({"erro": "não autenticado"}), 401

    pets = pet_model.listar_por_tutor(tutor_id)
    return jsonify([{"id": p.id, "nome": p.nome} for p in pets])