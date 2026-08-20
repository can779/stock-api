from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductSchema, UserCreate, UserLogin
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin
)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Stock API çalışıyor!"}


# -------------------------
# PRODUCTS
# -------------------------

@app.get("/products", response_model=list[ProductSchema])
def get_products(
    db: Session = Depends(get_db)
):
    products = db.scalars(
        select(Product)
    ).all()

    return products


@app.get("/products/{product_id}", response_model=ProductSchema)
def get_product(
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

    return product


@app.post("/products", response_model=ProductSchema)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
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
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
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


# -------------------------
# AUTHENTICATION
# -------------------------

@app.post("/auth/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == user.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu email zaten kayıtlı"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Kullanıcı başarıyla oluşturuldu",
        "username": new_user.username,
        "email": new_user.email
    }


@app.post("/auth/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == user.email)
    )

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Email veya şifre hatalı"
        )

    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Email veya şifre hatalı"
        )

    access_token = create_access_token({
        "sub": str(existing_user.id)
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }