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