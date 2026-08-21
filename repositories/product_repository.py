from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Product
from sqlalchemy.exc import SQLAlchemyError


def get_products(
    db: Session,
    page: int,
    limit: int,
    category: str | None = None,
    search: str | None = None,
    sort: str | None = None

):
    offset = (page - 1) * limit

    query = select(Product)

    if category:
        query = query.where(
            Product.category == category
        )


    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%")
        )

    if sort == "price_asc":
        query = query.order_by(
            Product.price.asc()
        )

    elif sort == "price_desc":
        query = query.order_by(
            Product.price.desc()
        )

    query = query.offset(offset).limit(limit)

    return db.scalars(query).all()

def get_product_by_id(
    db: Session,
    product_id: int
):
    return db.scalar(
        select(Product).where(Product.id == product_id)
    )


def create_product(
    db: Session,
    product: Product
):
    try:
        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    except SQLAlchemyError:
        db.rollback()
        raise


def update_product(
    db: Session,
    product: Product
):
    db.commit()
    db.refresh(product)

    return product


def delete_product(
    db: Session,
    product: Product
):
    db.delete(product)
    db.commit()