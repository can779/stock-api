from fastapi import FastAPI, Depends ,HTTPException
from sqlalchemy.orm import Session 

from database import get_db
from models import Product
from schemas import ProductCreate, ProductSchema

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Stock API çalışıyor!"}


@app.post("/products", response_model=ProductSchema)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = Product(
        name=product.name,
        price=product.price,
        description=product.description,
        stock=product.stock,
        category=product.category
        
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

from sqlalchemy import select

@app.get("/products", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    products = db.scalars(
        select(Product)
    ).all()

    return products

@app.get("/products/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    return product

@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.description = product.description
    existing_product.stock = product.stock
    existing_product.category = product.category
    

    db.commit()
    db.refresh(existing_product)

    return existing_product

@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    db.delete(product)
    db.commit()

    return {"message": "Ürün başarıyla silindi"}