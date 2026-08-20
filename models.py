from sqlalchemy import Column, Integer, String, Float , ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    stock = Column(Integer)
    category = Column(String, nullable=False)
    user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=False
)
    user = relationship("User", back_populates="products")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    products = relationship(
    "Product",
    back_populates="user"
)