"""Заполнение БД тестовыми категориями и товарами."""
from decimal import Decimal
from app import create_app, db
from app.models import Category, Product

app = create_app()

with app.app_context():
    if Category.query.count() > 0:
        print("Данные уже есть, пропускаем.")
    else:
        phones = Category(name="Смартфоны", description="Мобильные телефоны")
        laptops = Category(name="Ноутбуки", description="Портативные компьютеры")
        acc = Category(name="Аксессуары", description="Чехлы, зарядки, кабели")
        db.session.add_all([phones, laptops, acc])
        db.session.flush()

        db.session.add_all([
            Product(sku="SM-001", name="Смартфон Galaxy A15", category_id=phones.id, price=Decimal("19990.00"), stock=12),
            Product(sku="SM-002", name="Смартфон iPhone 13", category_id=phones.id, price=Decimal("54990.00"), stock=5),
            Product(sku="NB-001", name="Ноутбук Lenovo IdeaPad 3", category_id=laptops.id, price=Decimal("45990.00"), stock=7),
            Product(sku="NB-002", name="Ноутбук ASUS VivoBook", category_id=laptops.id, price=Decimal("62990.00"), stock=3),
            Product(sku="AC-001", name="Чехол силиконовый", category_id=acc.id, price=Decimal("790.00"), stock=50),
            Product(sku="AC-002", name="Кабель USB-C 1 м", category_id=acc.id, price=Decimal("490.00"), stock=30),
        ])
        db.session.commit()
        print("Тестовые данные добавлены.")