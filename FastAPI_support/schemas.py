from pydantic import BaseModel


class Product(BaseModel):
    code: int
    parent: int
    ispath: bool
    name: str
    quantity: int | None
    price: int | None

