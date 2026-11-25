from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    """Форма входа."""
    username = StringField("Логин", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    """Форма регистрации (доступна только администратору)."""
    username = StringField("Логин", validators=[DataRequired(), Length(3, 64)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password", message="Пароли не совпадают.")]
    )
    role = SelectField(
        "Роль",
        choices=[("cashier", "Кассир"), ("admin", "Администратор")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Зарегистрировать")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Такой логин уже занят.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Этот email уже используется.")

from wtforms import DecimalField, IntegerField, TextAreaField
from wtforms.validators import NumberRange


class CategoryForm(FlaskForm):
    """Форма категории."""
    name = StringField("Название", validators=[DataRequired(), Length(2, 100)])
    description = TextAreaField("Описание")
    submit = SubmitField("Сохранить")


class ProductForm(FlaskForm):
    """Форма товара."""
    sku = StringField("Артикул", validators=[DataRequired(), Length(1, 32)])
    name = StringField("Наименование", validators=[DataRequired(), Length(2, 200)])
    category_id = SelectField("Категория", coerce=int, validators=[DataRequired()])
    price = DecimalField("Цена, ₽", places=2, validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Остаток", validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField("Ед. изм.", validators=[DataRequired(), Length(1, 16)], default="шт")
    description = TextAreaField("Описание")
    submit = SubmitField("Сохранить")

    def validate_sku(self, sku):
        # Проверка уникальности артикула — при редактировании пропускаем текущий товар
        from app.models import Product
        product = Product.query.filter_by(sku=sku.data).first()
        if product and getattr(self, "_product_id", None) != product.id:
            raise ValidationError("Товар с таким артикулом уже существует.")
class AddToCartForm(FlaskForm):
    """Добавление товара в корзину."""
    product_id = IntegerField("Товар", validators=[DataRequired()])
    quantity = IntegerField("Количество", validators=[DataRequired(), NumberRange(min=1, max=9999)], default=1)
    submit = SubmitField("Добавить")


class CheckoutForm(FlaskForm):
    """Оформление продажи."""
    payment_method = SelectField(
        "Способ оплаты",
        choices=[("cash", "Наличные"), ("card", "Карта")],
        validators=[DataRequired()]
    )
    discount = DecimalField("Скидка, ₽", places=2, default=0, validators=[NumberRange(min=0)])
    submit = SubmitField("Оформить продажу")