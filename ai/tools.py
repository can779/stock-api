from sqlalchemy.orm import Session

from repositories.product_repository import get_products , get_product_by_name

from ai.rag.rag_service import answer_with_rag

def search_company_policy(
    question: str
):
    return answer_with_rag(
        question
    )

search_company_policy_tool = {
    "type": "function",
    "function": {
        "name": "search_company_policy",
        "description": "Şirketin stok politikalarını ve kurallarını dokümanlardan getirir. Minimum stok seviyesi, yeniden sipariş koşulları veya bir ürün kategorisi için belirlenmiş stok politikası sorularında kullanılmalıdır. Bir ürünün mevcut stok miktarı bu tool ile öğrenilmez.",        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Şirket politikası hakkında cevaplanması gereken soru"
                }
            },
            "required": ["question"]
        }
    }
}


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
        "description": "Veritabanındaki ürünlerin listesini, fiyatlarını, stok miktarlarını ve kategorilerini getirir.",
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
        "description": "Belirtilen ürünün veritabanındaki mevcut fiyatını, stok miktarını ve kategorisini getirir. Bir ürünün mevcut stok miktarını öğrenmek için kullanılır; şirketin minimum stok politikasını öğrenmek için kullanılmaz.",
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

def get_low_stock_products(
    db: Session
):
    products = get_products(
        db,
        page=1,
        limit=100
    )

    low_stock_products = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "category": product.category
        }
        for product in products
        if product.stock <= 10
    ]

    return low_stock_products

get_low_stock_products_tool = {
    "type": "function",
    "function": {
        "name": "get_low_stock_products",
        "description": "Stok miktarı 10 veya daha az olan ürünlerin listesini getirir. Bir ürünün şirket politikasındaki minimum stok seviyesinin altında olup olmadığını belirlemek için kullanılmaz; bu tür karşılaştırmalar için ürün stok bilgisi ile şirket politikası birlikte değerlendirilmelidir.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}