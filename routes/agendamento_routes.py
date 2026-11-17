from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash,
)
from models.agendamento_model import (
    AgendamentoModel, Agendamento,
    AgendamentoError, AgendamentoDuplicadoError,
    PetInexistenteError, StatusInvalidoError,
    STATUS_VALIDOS,
)
from models.pet_model import PetModel

agendamento_bp = Blueprint("agendamento", __name__)
ag_model = AgendamentoModel()
pet_model = PetModel()


def _login_obrigatorio():
    return "user_id" not in session


# ------------------------------------------------------------
# GET /agendamentos
# ------------------------------------------------------------
@agendamento_bp.route("/agendamentos")
def listar_agendamentos():
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    filtro_data = request.args.get("data", "").strip() or None
    filtro_status = request.args.get("status", "").strip() or None

    lista = ag_model.listar_todos(data=filtro_data, status=filtro_status)
    pets = pet_model.listar_todos()

    return render_template(
        "pages/a.html",
        agendamentos=lista,
        pets=pets,
        filtro_data=filtro_data or "",
        filtro_status=filtro_status or "",
        status_validos=sorted(STATUS_VALIDOS),
    )


# ------------------------------------------------------------
# POST /agendamentos
# ------------------------------------------------------------
@agendamento_bp.route("/agendamentos", methods=["POST"])
def cadastrar_agendamento():
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    try:
        ag = Agendamento(
            id=None,
            pet_id=int(request.form["pet"]) if request.form.get("pet") else 0,
            servico=request.form["servico"],
            data=request.form["data"],
            horario=request.form["hora"],
            observacoes=request.form.get("obs", ""),
        )
        ag_model.cadastrar(ag)
        return jsonify({"ok": True, "mensagem": "Agendamento criado com sucesso!"})
    except AgendamentoDuplicadoError as e:
        return jsonify({"erro": str(e)}), 400
    except PetInexistenteError as e:
        return jsonify({"erro": str(e)}), 400
    except StatusInvalidoError as e:
        return jsonify({"erro": str(e)}), 400
    except AgendamentoError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro inesperado: {e}"}), 500


# ------------------------------------------------------------
# POST /agendamentos/<id>/status/<novo>
# ------------------------------------------------------------
@agendamento_bp.route(
    "/agendamentos/<int:ag_id>/status/<string:novo>", methods=["POST"]
)
def alterar_status(ag_id, novo):
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    try:
        ag_model.atualizar_status(ag_id, novo)
        flash(f"Status alterado para '{novo}'.", "sucesso")
    except StatusInvalidoError as e:
        flash(str(e), "erro")

    return redirect(url_for("agendamento.listar_agendamentos"))


# ------------------------------------------------------------
# GET /api/agendamentos (JSON direto com pet_nome)
# ------------------------------------------------------------
@agendamento_bp.route("/api/agendamentos")
def api_listar_agendamentos():
    if _login_obrigatorio():
        return jsonify({"erro": "não autenticado"}), 401

    filtro_data = request.args.get("data", "").strip() or None
    filtro_status = request.args.get("status", "").strip() or None

    try:
        lista = ag_model.listar_todos(data=filtro_data, status=filtro_status)
    except StatusInvalidoError as e:
        return jsonify({"erro": str(e)}), 400

    return jsonify(lista)