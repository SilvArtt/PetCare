from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash,
)
from models.tutor_model import TutorModel, Tutor

tutor_bp = Blueprint("tutor", __name__)
tutor_model = TutorModel()


def _login_obrigatorio():
    return "user_id" not in session


# ------------------------------------------------------------
# GET /tutores
# ------------------------------------------------------------
@tutor_bp.route("/tutores")
def listar_tutores():
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    filtro = request.args.get("q", "").strip()
    tutores = tutor_model.listar(filtro=filtro)

    return render_template(
        "pages/t.html",
        tutores=tutores,
        filtro=filtro,
    )


# ------------------------------------------------------------
# POST /tutor (ação do formulário t.html)
# ------------------------------------------------------------
@tutor_bp.route("/tutor", methods=["POST"])
def cadastrar_tutor():
    if _login_obrigatorio():
        return redirect(url_for("auth.index"))

    tutor = Tutor(
        id=None,
        nome=request.form["nome"].strip(),
        cpf=request.form["cpf"].strip(),
        data_nascimento=request.form.get("data_nascimento", ""),
        email=request.form.get("email", ""),
        telefone=request.form.get("telefone", ""),
        cep=request.form.get("cep", ""),
        numero=request.form.get("numero", ""),
        rua=request.form.get("rua", ""),
        complemento=request.form.get("complemento", ""),
        bairro=request.form.get("bairro", ""),
        cidade=request.form.get("cidade", ""),
        estado=request.form.get("estado", ""),
    )

    novo_id = tutor_model.cadastrar(tutor)
    if novo_id is None:
        flash("CPF já cadastrado.", "erro")
    else:
        flash("Tutor cadastrado com sucesso!", "sucesso")

    return redirect(url_for("tutor.listar_tutores"))


# ------------------------------------------------------------
# GET /api/tutores (para JS)
# ------------------------------------------------------------
@tutor_bp.route("/api/tutores")
def api_listar_tutores():
    if _login_obrigatorio():
        return jsonify({"erro": "não autenticado"}), 401

    tutores = tutor_model.listar_todos()
    return jsonify([
        {
            "id": t.id,
            "nome": t.nome,
            "cpf": t.cpf,
            "email": t.email,
            "telefone": t.telefone,
            "cidade": t.cidade,
            "estado": t.estado,
        }
        for t in tutores
    ])


# ------------------------------------------------------------
# POST /api/tutores/editar/<id>
# ------------------------------------------------------------
@tutor_bp.route("/api/tutores/editar/<int:tutor_id>", methods=["POST"])
def api_editar_tutor(tutor_id):
    if _login_obrigatorio():
        return jsonify({"erro": "não autenticado"}), 401

    dados = request.get_json(silent=True) or request.form.to_dict()
    atual = tutor_model.buscar_por_id(tutor_id)
    if atual is None:
        return jsonify({"erro": "tutor não encontrado"}), 404

    for campo in (
        "nome", "cpf", "data_nascimento", "email", "telefone",
        "cep", "numero", "rua", "complemento", "bairro", "cidade", "estado",
    ):
        if campo in dados:
            setattr(atual, campo, dados[campo])

    ok = tutor_model.atualizar(atual)
    if not ok:
        return jsonify({"erro": "CPF duplicado ou falha ao atualizar"}), 400
    return jsonify({"ok": True, "id": tutor_id})


# ------------------------------------------------------------
# DELETE /api/tutores/<id>
# ------------------------------------------------------------
@tutor_bp.route("/api/tutores/<int:tutor_id>", methods=["DELETE"])
def api_deletar_tutor(tutor_id):
    if _login_obrigatorio():
        return jsonify({"erro": "não autenticado"}), 401

    ok = tutor_model.excluir(tutor_id)
    if not ok:
        return jsonify({
            "erro": "Não foi possível excluir: tutor possui pets vinculados."
        }), 409
    return jsonify({"ok": True})