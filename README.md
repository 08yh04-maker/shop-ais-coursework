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
(будет дополняться)