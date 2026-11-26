# АИС учета продажи товаров магазина «ТехноМир»

Курсовая работа по дисциплине «Интернет-программирование».
ТулГУ, Институт прикладной математики и компьютерных наук.

## Стек
- Python 3.11+, Flask
- PostgreSQL 16
- SQLAlchemy, Flask-Migrate
- Flask-Login, Flask-WTF
- HTML5, CSS3, JavaScript (Vanilla)
- pytest

## Запуск (через Docker)

1. Скопировать `.env.example` в `.env` и задать `SECRET_KEY`.
2. Поднять БД: `docker compose up -d`
3. Создать venv и установить зависимости:
python -m venv .venv
.venv\Scripts\activate # Windows
pip install -r requirements.txt
4. Применить миграции (после появления моделей):
flask db upgrade
5. Запустить: `flask run` или `python run.py`
6. Открыть http://127.0.0.1:5000

## Структура
shop-ais-coursework/
├── app/
│   ├── __init__.py            # Инициализация Flask, БД, LoginManager, CSRF
│   ├── config.py              # Настройки (строка подключения к PostgreSQL)
│   ├── models.py              # Модели БД (User, Category, Product, Sale, SaleItem)
│   ├── forms.py               # Формы WTForms (Валидация, Загрузка фото)
│   ├── utils.py               # Утилиты (сохранение/удаление картинок)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Вход, выход, регистрация (роли)
│   │   ├── products.py        # CRUD товаров и категорий
│   │   ├── sales.py           # Корзина, оформление чека, списание остатков
│   │   └── reports.py         # Отчеты (выручка, топ-товаров)
│   ├── templates/             # HTML-шаблоны (Jinja2)
│   │   ├── base.html          # Базовый шаблон (шапка, подвал, flash-сообщения)
│   │   ├── index.html         # Главная страница (Дашборд с плитками)
│   │   ├── auth/              # Шаблоны входа и регистрации
│   │   ├── products/          # Шаблоны списка и формы товаров
│   │   ├── categories/        # Шаблоны списка и формы категорий
│   │   ├── sales/             # Шаблоны корзины, оформления, чека
│   │   └── reports/           # Шаблон отчетов
│   └── static/                # Статика
│       ├── css/style.css      # Все стили
│       ├── js/main.js         # Скрипт автоскрытия уведомлений
│       └── uploads/           # Папка для загруженных фото товаров
├── migrations/                # Файлы миграций Alembic (версии БД)
├── .env                       # Секреты (НЕ В ГИТЕ)
├── .env.example               # Пример настроек
├── .gitignore                 # Исключения для Git (venv, .env, uploads)
├── create_admin.py            # Скрипт создания админа (admin / admin123)
├── seed_data.py               # Скрипт заполнения БД тестовыми товарами
├── requirements.txt           # Список зависимостей (pip install -r ...)
├── docker-compose.yml         # Конфиг для запуска PostgreSQL в Docker (для ноута)
├── README.md                  # Инструкция по запуску
└── run.py                     # Точка входа (создает app)
