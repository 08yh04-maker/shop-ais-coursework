from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    """Фабрика приложения."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Для доступа к этой странице войдите в систему."
    login_manager.login_message_category = "warning"

    # Импорт моделей нужен, чтобы Alembic их увидел
    from app import models  # noqa: F401

    # Регистрация blueprint'ов
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return render_template("index.html")

    return app