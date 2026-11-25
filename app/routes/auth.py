from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.forms import LoginForm, RegistrationForm
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Добро пожаловать, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("Неверный логин или пароль.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if not current_user.is_admin:
        flash("Регистрация доступна только администратору.", "danger")
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Пользователь {user.username} создан.", "success")
        return redirect(url_for("auth.register"))

    return render_template("auth/register.html", form=form)