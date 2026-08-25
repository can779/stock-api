from sqlalchemy.orm import Session

from repositories.product_repository import (
    get_products,
    get_product_by_name
)

from ai.rag.rag_service import answer_with_rag

from services.erp_service import get_erp_product


# ============================================================
# COMPANY POLICY / RAG
# ============================================================

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
        "description": (
            "Şirketin stok politikalarını ve kurallarını "
            "dokümanlardan getirir. Minimum stok seviyesi, "
            "yeniden sipariş koşulları ve kategori bazlı "
            "stok politikaları için kullanılır. "
            "Bir ürünün mevcut stok miktarını bu araçtan öğrenme."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "Şirket politikası hakkında "
                        "cevaplanması gereken soru"
                    )
                }
            },
            "required": [
                "question"
            ]
        }
    }
}


# ============================================================
# ALL STOCK PRODUCTS
# ============================================================

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
        "description": (
            "Veritabanındaki ürünlerin listesini, "
            "fiyatlarını, stok miktarlarını ve "
            "kategorilerini getirir."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


# ============================================================
# DATABASE PRODUCT STOCK
# ============================================================

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
        "description": (
            "Doğrudan uygulama veritabanındaki ürünün "
            "mevcut stok miktarını getirir. "
            "Bu araç yalnızca doğrudan veritabanı sorguları "
            "için kullanılır. "
            "Kullanıcı ERP sistemindeki güncel ürün veya "
            "stok bilgisini soruyorsa bu aracı kullanma; "
            "get_erp_product aracını kullan."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": (
                        "Aranacak ürünün adı"
                    )
                }
            },
            "required": [
                "product_name"
            ]
        }
    }
}


# ============================================================
# ERP PRODUCT
# ============================================================

def get_erp_product_tool_function(
    product_name: str
):
    return get_erp_product(
        product_name
    )


get_erp_product_tool = {
    "type": "function",
    "function": {
        "name": "get_erp_product",
        "description": (
            "ERP sistemindeki ürünün güncel stok, fiyat, "
            "kategori ve ürün bilgilerini getirir. "
            "Kullanıcı ERP, kurumsal sistem, güncel stok "
            "veya ürünün mevcut stok durumu hakkında soru "
            "soruyorsa BU TOOL KULLANILMALIDIR. "
            "Şirketin minimum stok politikası bu tool ile "
            "öğrenilmez. Minimum stok seviyesi ve yeniden "
            "sipariş kuralları için "
            "search_company_policy tool'u kullanılmalıdır."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": (
                        "ERP'de aranacak ürünün adı"
                    )
                }
            },
            "required": [
                "product_name"
            ]
        }
    }
}


# ============================================================
# LOW STOCK PRODUCTS
# ============================================================

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
        "description": (
            "Stok miktarı 10 veya daha az olan ürünlerin "
            "listesini getirir. "
            "Şirket politikasındaki minimum stok seviyesini "
            "belirlemek için kullanılmaz. "
            "Bir ürünün şirket politikasındaki minimum stok "
            "seviyesinin altında olup olmadığını belirlemek "
            "için ürün stok bilgisi ile şirket politikası "
            "birlikte değerlendirilmelidir."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}