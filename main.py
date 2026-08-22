from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import User

from schemas import (
    ProductCreate,
    ProductSchema,
    ProductUpdate,
    UserCreate,
    UserLogin,
    AIRequest,
    AIResponse
)

from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin
)

from services.product_service import (
    create_product_service,
    get_products_service,
    get_product_service,
    update_product_service,
    delete_product_service
)
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
import logging

from ai.ai_service import chat_with_ai
from ai.llm_service import ask_llm


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database hatası oluştu"
        }
    )


@app.get("/")
def home():
    return {"message": "Stock API çalışıyor!"}


# =========================================================
# PRODUCTS
# =========================================================

@app.post(
    "/products",
    response_model=ProductSchema,
    status_code=201
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_product_service(
        db,
        product,
        current_user.id
    )


@app.get(
    "/products",
    response_model=list[ProductSchema]
)
def get_products_endpoint(
    page: int = 1,
    limit: int = 10,
    category: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_products_service(
        db,
        page,
        limit,
        category,
        search,
        sort
    )


@app.get(
    "/products/{product_id}",
    response_model=ProductSchema
)
def get_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = get_product_service(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductSchema
)
def update_product_endpoint(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    updated_product = update_product_service(
        db,
        product_id,
        product
    )

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    return updated_product


@app.delete(
    "/products/{product_id}",
    status_code=204
)
def delete_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    deleted = delete_product_service(
        db,
        product_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    return


# =========================================================
# AUTH
# =========================================================

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

    logger.info(
        "Kullanıcı giriş yaptı: %s",
        existing_user.email
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post(
    "/ai/chat",
    response_model=AIResponse
)
def ai_chat(
    request: AIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = chat_with_ai(
        db,
        request.message
    )

    return {
        "response": response
    }