from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    stock: int
    category = str

class ProductSchema(BaseModel):
    id: int
    name: str
    price: float
    description: str
    stock: int
    category = str

    model_config = ConfigDict(from_attributes=True)