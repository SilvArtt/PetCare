from flask import Flask, render_template, session, redirect, url_for
from datetime import timedelta
import os

# Importa os Blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.tutor_routes import tutor_bp
from routes.pet_routes import pet_bp
from routes.agendamento_routes import agendamento_bp

# Inicialização do Flask
app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
    template_folder="templates"
)

# Configurações de segurança / sessão
app.secret_key = "sua_chave_secreta_super_segura_aqui_mude_isso"
app.permanent_session_lifetime = timedelta(minutes=30)

# Registro dos Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(tutor_bp)
app.register_blueprint(pet_bp)
app.register_blueprint(agendamento_bp)

# Rota raiz para redirecionar corretamente
@app.route("/")
def raiz():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.index"))

if __name__ == "__main__":
    app.run(debug=True)