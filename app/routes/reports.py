from datetime import datetime, timedelta
from decimal import Decimal

from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import Sale, SaleItem, Product, Category

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _get_period():
    """Возвращает (start_date, end_date) из GET-параметров или последние 30 дней."""
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if start_str and end_str:
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d")
            end = datetime.strptime(end_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            return start, end, start_str, end_str
        except ValueError:
            pass

    # По умолчанию — последние 30 дней
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    return start, end, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


@reports_bp.route("/")
@login_required
def index():
    if not current_user.is_admin:
        abort(403)

    start, end, start_str, end_str = _get_period()

    # 1. Общая выручка и количество чеков за период
    summary = db.session.query(
        func.coalesce(func.sum(Sale.total), 0).label("revenue"),
        func.count(Sale.id).label("sales_count")
    ).filter(Sale.created_at.between(start, end)).first()

    revenue = Decimal(summary.revenue)
    sales_count = summary.sales_count
    avg_check = revenue / sales_count if sales_count > 0 else Decimal("0.00")

    # 2. Топ-5 товаров по количеству проданных единиц
    top_products = db.session.query(
        Product.name,
        func.sum(SaleItem.quantity).label("total_qty"),
        func.sum(SaleItem.quantity * SaleItem.price).label("total_sum")
    ).join(SaleItem).join(Sale).filter(
        Sale.created_at.between(start, end)
    ).group_by(Product.id, Product.name).order_by(
        func.sum(SaleItem.quantity).desc()
    ).limit(5).all()

    # 3. Выручка по категориям
    category_stats = db.session.query(
        Category.name,
        func.sum(SaleItem.quantity * SaleItem.price).label("total_sum")
    ).join(Product, Product.category_id == Category.id) \
     .join(SaleItem, SaleItem.product_id == Product.id) \
     .join(Sale, Sale.id == SaleItem.sale_id) \
     .filter(Sale.created_at.between(start, end)) \
     .group_by(Category.id, Category.name) \
     .order_by(func.sum(SaleItem.quantity * SaleItem.price).desc()).all()

    # 4. Товары с низким остатком (не зависит от периода)
    low_stock = Product.query.filter(Product.stock <= 5).order_by(Product.stock).all()

    return render_template(
        "reports/index.html",
        start_str=start_str,
        end_str=end_str,
        revenue=revenue,
        sales_count=sales_count,
        avg_check=avg_check,
        top_products=top_products,
        category_stats=category_stats,
        low_stock=low_stock,
    )