from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
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

    # Регистрация blueprint'ов (добавим по мере готовности)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return "АИС «ТехноМир» — каркас работает."

    return app