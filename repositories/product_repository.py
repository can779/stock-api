from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Product
from sqlalchemy.exc import SQLAlchemyError


def get_products(db: Session):
    return db.scalars(
        select(Product)
    ).all()


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