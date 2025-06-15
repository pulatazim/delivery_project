from pydantic import BaseModel
from typing import List, Optional


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': "sayitkamol",
                'email': 'sayitkamol@gmail.com',
                'password': 'qiyinparol',
                'is_staff': False,
                'is_active': True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = '53bd3497650a751cf67c8f61fbc5f04da04361d958fd43df28618c5b3be1c01b'


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    quantity: int
    order_status: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 1
            }
        }


class OrderStatusModel(BaseModel):
    oder_status: Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": "PENDING"
            }
        }


class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                'name': 'uzbek plov',
                'price': 30000
            }
        }

