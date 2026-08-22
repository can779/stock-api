from sqlalchemy.orm import Session

from repositories.product_repository import get_products , get_product_by_name


def get_stock_products(
    db: Session,
    page: int = 1,
    limit: int = 100
):
    products = get_products(
        db,
        page,
        limit
    )

    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "category": product.category
        }
        for product in products
    ]

get_stock_products_tool = {
    "type": "function",
    "function": {
        "name": "get_stock_products",
        "description": "Veritabanındaki ürünleri, fiyatlarını, stok miktarlarını ve kategorilerini getirir.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def get_product_stock(
    db: Session,
    product_name: str
):
    product = get_product_by_name(
        db,
        product_name
    )

    if product is None:
        return {
            "error": "Ürün bulunamadı"
        }

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "category": product.category
    }

get_product_stock_tool = {
    "type": "function",
    "function": {
        "name": "get_product_stock",
        "description": "Belirtilen ürünün fiyatını, stok miktarını ve kategorisini getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Aranacak ürünün adı"
                }
            },
            "required": ["product_name"]
        }
    }
}