from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException


from models import Order, User, Product
from schemas import OrderModel, OrderStatusModel
from database import session, engine

order_routes = APIRouter(
    prefix="/order",
)

session = session(bind=engine)


@order_routes.get("/")
async def welcome_page(Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    return {"message": "Bu order route sahifasi"}


@order_routes.post("/make", status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    print(current_user)
    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        quantity=order.quantity
        # product = order.product_id
    )
    new_order.user = user
    session.add(new_order)
    session.commit()

    response = {
        "id": new_order.id,
        'quantity': new_order.quantity,
        'order_status': new_order.order_statuses
    }
    return jsonable_encoder(response)

