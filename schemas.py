from pydantic import BaseModel, ConfigDict , Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    description: str = Field(min_length=5, max_length=500)
    stock: int = Field(ge=0)
    category: str = Field(min_length=2, max_length=50)


class ProductSchema(BaseModel):
    id: int
    name: str
    price: float
    description: str
    stock: int
    category: str
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    price: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=5, max_length=500)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=2, max_length=50)

class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)