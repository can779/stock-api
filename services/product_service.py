from sqlalchemy.orm import Session

from models import Product
from schemas import ProductCreate, ProductUpdate

from repositories.product_repository import (
    get_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)
import logging

logger = logging.getLogger(__name__)

def create_product_service(
    db: Session,
    product_data: ProductCreate,
    user_id: int
):
    new_product = Product(
        name=product_data.name,
        price=product_data.price,
        description=product_data.description,
        stock=product_data.stock,
        category=product_data.category,
        user_id=user_id
    )

    result = create_product(db, new_product)

    logger.info(
        "Ürün oluşturuldu: product_id=%s user_id=%s",
        result.id,
        user_id
    )

    return result

def get_products_service(
    db: Session
):
    return get_products(db)


def get_product_service(
    db: Session,
    product_id: int
):
    return get_product_by_id(db, product_id)


def update_product_service(
    db: Session,
    product_id: int,
    product_data: ProductUpdate
):
    product = get_product_by_id(db, product_id)

    if product is None:
        return None

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(product, field, value)

    return update_product(db, product)


def delete_product_service(
    db: Session,
    product_id: int
):
    product = get_product_by_id(db, product_id)

    if product is None:
        return None

    delete_product(db, product)

    return True