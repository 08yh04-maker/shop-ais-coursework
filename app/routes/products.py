from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.forms import CategoryForm, ProductForm
from app.models import Category, Product
from app.utils import save_image, delete_image

products_bp = Blueprint("products", __name__, url_prefix="/products")
categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


# ---------- Категории ----------

@categories_bp.route("/")
@login_required
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template("categories/list.html", categories=categories)


@categories_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_category():
    if not current_user.is_admin:
        abort(403)
    form = CategoryForm()
    if form.validate_on_submit():
        db.session.add(Category(name=form.name.data, description=form.description.data))
        db.session.commit()
        flash("Категория добавлена.", "success")
        return redirect(url_for("categories.list_categories"))
    return render_template("categories/form.html", form=form, title="Новая категория")


@categories_bp.route("/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        abort(403)
    category = db.get_or_404(Category, category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash("Категория обновлена.", "success")
        return redirect(url_for("categories.list_categories"))
    return render_template("categories/form.html", form=form, title="Редактирование категории")


@categories_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        abort(403)
    category = db.get_or_404(Category, category_id)
    if category.products.count() > 0:
        flash("Нельзя удалить категорию, в которой есть товары.", "danger")
        return redirect(url_for("categories.list_categories"))
    db.session.delete(category)
    db.session.commit()
    flash("Категория удалена.", "info")
    return redirect(url_for("categories.list_categories"))


# ---------- Товары ----------

@products_bp.route("/")
@login_required
def list_products():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) | (Product.sku.ilike(f"%{q}%"))
        )
    products = query.order_by(Product.name).all()
    return render_template("products/list.html", products=products, q=q)


@products_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_product():
    if not current_user.is_admin:
        abort(403)
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    if form.validate_on_submit():
        product = Product(
            sku=form.sku.data,
            name=form.name.data,
            category_id=form.category_id.data,
            price=form.price.data,
            stock=form.stock.data,
            unit=form.unit.data,
            description=form.description.data,
        )
        if form.image.data:
            product.image_filename = save_image(form.image.data)
        db.session.add(product)
        db.session.commit()
        flash("Товар добавлен.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", form=form, title="Новый товар")


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        abort(403)
    product = db.get_or_404(Product, product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    form._product_id = product.id  # чтобы validate_sku пропустил текущий товар
    if form.validate_on_submit():
        product.sku = form.sku.data
        product.name = form.name.data
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.unit = form.unit.data
        product.description = form.description.data
        if form.image.data:
            delete_image(product.image_filename)
            product.image_filename = save_image(form.image.data)
        db.session.commit()
        flash("Товар обновлён.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", form=form, title="Редактирование товара")


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        abort(403)
    product = db.get_or_404(Product, product_id)
    if product.sale_items.count() > 0:
        flash("Нельзя удалить товар, который уже продавался.", "danger")
        return redirect(url_for("products.list_products"))
    delete_image(product.image_filename)
    db.session.delete(product)
    db.session.commit()
    flash("Товар удалён.", "info")
    return redirect(url_for("products.list_products"))