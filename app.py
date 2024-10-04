"""App de autenticação"""

from flask import Flask, jsonify, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models.user import User
from database import db

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """Funtion load user"""
    return User.query.get(user_id)


@app.route("/login", methods=["POST"])
def login():
    """Funtion to login."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return jsonify({"message": "Autenticação realizada com sucesso!"})

    return jsonify({"message": "Credenciais inválidas!"}), 400


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Funtion to logout a user. Must be login to use this route"""
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})


@app.route("/user", methods=["POST"])
def create_user():
    """Funtion to create a user"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Cadastro realizado com sucesso!"})

    return jsonify({"message": "Dados invalidos!"}), 400


@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    """Funtion to get logged user."""
    user = User.query.get(id_user)
    if user:
        return {"username": user.username}

    return jsonify({"message": "Usuario não encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    """Funtion update a user"""
    data = request.json
    user = User.query.get(id_user)

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} atualizado com sucesso"})

    return jsonify({"message": "Usuario não encontrado"}), 404


@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    """Funtion to delete a user"""
    user = User.query.get(id_user)

    if id_user == current_user.id:
        return jsonify({"message": "Deleção não permitida"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": f"Usuário {id_user} deletado com sucesso"})

    return jsonify({"message": "Usuario não encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
