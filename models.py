from sqlalchemy import Column, Integer, String, Float
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    stock = Column(Integer)
    category = Column(String)