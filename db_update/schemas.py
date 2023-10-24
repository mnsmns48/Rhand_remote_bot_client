from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    code: int
    parent: int
    ispath: bool
    name: str
    quantity: int | None
    price: int | None

