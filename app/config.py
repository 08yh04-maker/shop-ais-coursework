import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Базовая конфигурация приложения."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://shop_user:shop_pass@localhost:5432/shop_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True