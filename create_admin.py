"""Одноразовый скрипт: создаёт администратора, если его нет."""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    if User.query.filter_by(username="admin").first():
        print("Администратор уже существует.")
    else:
        admin = User(username="admin", email="admin@technomir.ru", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Администратор создан: admin / admin123")