from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_required, current_user

from app import db
from app.forms import AddToCartForm, CheckoutForm
from app.models import Product, Sale, SaleItem

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

CART_KEY = "cart"  # корзина в сессии: {product_id: quantity}


def _get_cart() -> dict:
    """Возвращает корзину из сессии (создаёт пустую при отсутствии)."""
    return session.setdefault(CART_KEY, {})


def _cart_items() -> list[dict]:
    """Собирает позиции корзины с данными товаров и суммами."""
    cart = _get_cart()
    items = []
    for pid_str, qty in cart.items():
        product = db.session.get(Product, int(pid_str))
        if not product:
            continue
        items.append({
            "product": product,
            "quantity": qty,
            "subtotal": product.price * qty,
        })
    return items


def _cart_total(items: list[dict]) -> Decimal:
    return sum((item["subtotal"] for item in items), Decimal("0.00"))


# ---------- Корзина ----------

@sales_bp.route("/cart")
@login_required
def cart():
    items = _cart_items()
    total = _cart_total(items)
    form = AddToCartForm()
    return render_template("sales/cart.html", items=items, total=total, form=form)


@sales_bp.route("/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    form = AddToCartForm()
    if form.validate_on_submit():
        product = db.session.get(Product, form.product_id.data)
        if not product:
            flash("Товар не найден.", "danger")
            return redirect(url_for("products.list_products"))
        cart = _get_cart()
        key = str(product.id)
        new_qty = cart.get(key, 0) + form.quantity.data
        if new_qty > product.stock:
            flash(f"На складе только {product.stock} {product.unit}.", "warning")
            return redirect(url_for("products.list_products"))
        cart[key] = new_qty
        session.modified = True
        flash(f"«{product.name}» добавлен в корзину.", "success")
    return redirect(url_for("sales.cart"))


@sales_bp.route("/cart/update/<int:product_id>", methods=["POST"])
@login_required
def update_cart(product_id):
    qty = request.form.get("quantity", type=int, default=1)
    product = db.session.get(Product, product_id)
    cart = _get_cart()
    key = str(product_id)

    if not product or key not in cart:
        abort(404)

    if qty <= 0:
        cart.pop(key, None)
    elif qty > product.stock:
        flash(f"На складе только {product.stock} {product.unit}.", "warning")
    else:
        cart[key] = qty

    session.modified = True
    return redirect(url_for("sales.cart"))


@sales_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    return redirect(url_for("sales.cart"))


@sales_bp.route("/cart/clear", methods=["POST"])
@login_required
def clear_cart():
    session.pop(CART_KEY, None)
    flash("Корзина очищена.", "info")
    return redirect(url_for("sales.cart"))


# ---------- Оформление ----------

@sales_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = _cart_items()
    if not items:
        flash("Корзина пуста.", "warning")
        return redirect(url_for("sales.cart"))

    total = _cart_total(items)
    form = CheckoutForm()

    if form.validate_on_submit():
        discount = form.discount.data or Decimal("0.00")
        if discount > total:
            flash("Скидка не может превышать сумму чека.", "danger")
            return render_template("sales/checkout.html", form=form, items=items, total=total)

        # Проверяем остатки перед списанием
        for item in items:
            if item["quantity"] > item["product"].stock:
                flash(f"«{item['product'].name}»: на складе только {item['product'].stock}.", "danger")
                return render_template("sales/checkout.html", form=form, items=items, total=total)

        try:
            sale = Sale(
                seller_id=current_user.id,
                payment_method=form.payment_method.data,
                discount=discount,
                total=total - discount,
            )
            db.session.add(sale)
            db.session.flush()  # получаем sale.id

            for item in items:
                product = item["product"]
                db.session.add(SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    price=product.price,
                ))
                product.stock -= item["quantity"]

            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Ошибка при оформлении продажи. Попробуйте ещё раз.", "danger")
            return render_template("sales/checkout.html", form=form, items=items, total=total)

        session.pop(CART_KEY, None)
        flash(f"Продажа №{sale.id} оформлена.", "success")
        return redirect(url_for("sales.receipt", sale_id=sale.id))

    return render_template("sales/checkout.html", form=form, items=items, total=total)


# ---------- Чек и история ----------

@sales_bp.route("/")
@login_required
def list_sales():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template("sales/list.html", sales=sales)


@sales_bp.route("/<int:sale_id>")
@login_required
def receipt(sale_id):
    sale = db.get_or_404(Sale, sale_id)
    return render_template("sales/receipt.html", sale=sale)