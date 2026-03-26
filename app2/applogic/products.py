from database import SessionLocal
from models import Product


# ── READ ──────────────────────────────────────────────────────────────────────

def get_all_products():
    db = SessionLocal()
    products = db.query(Product).order_by(Product.product_id).all()
    db.close()
    return products


def get_product_by_id(product_id):
    db = SessionLocal()
    product = db.get(Product, product_id)
    db.close()
    return product


def get_products_by_category(category):
    db = SessionLocal()
    products = (
        db.query(Product)
        .filter(Product.product_category == category)
        .order_by(Product.product_id)
        .all()
    )
    db.close()
    return products


# ── CREATE ────────────────────────────────────────────────────────────────────

def create_product(name, price, description=None, category=None):
    db = SessionLocal()
    product = Product(
        product_name        = name,
        product_description = description,
        product_category    = category,
        product_price       = price,
    )
    db.add(product)
    db.commit()
    db.close()


# ── UPDATE ────────────────────────────────────────────────────────────────────

def update_product(product_id, name, price, description=None, category=None):
    db = SessionLocal()
    product = db.get(Product, product_id)
    if product is None:
        db.close()
        return None
    product.product_name        = name
    product.product_price       = price
    product.product_description = description
    product.product_category    = category
    db.commit()
    db.close()


# ── DELETE ────────────────────────────────────────────────────────────────────

def delete_product(product_id):
    db = SessionLocal()
    product = db.get(Product, product_id)
    if product is None:
        db.close()
        return False
    db.delete(product)
    db.commit()
    db.close()
    return True