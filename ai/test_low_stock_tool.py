from database import SessionLocal

from ai.tools import get_low_stock_products


db = SessionLocal()

try:
    result = get_low_stock_products(db)

    print("DÜŞÜK STOKLU ÜRÜNLER:")

    for product in result:
        print(product)

finally:
    db.close()