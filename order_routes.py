

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
        quantity=order.quantity,
        # product = order.product_id
    )
    new_order.user = user
    session.add(new_order)
    session.commit()
    data = {
        "success": True,
        "code": 201,
        "message": "Order created successfully",
        "data": {
            "id": new_order.id,
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_statuses,
        }
    }

    response = data
    return jsonable_encoder(response)


@order_routes.get('/list')
async def list_all_order(Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()
        custom_data = [
            {
                'id': order.id,
                'user': {
                    'id': order.user.id,
                    'username': order.user.username,
                    'email': order.user.email
                },
                'product_id': order.product_id,
                'quantity': order.quantity,
                'order_statuses': order.order_statuses.value,
            }
            for order in orders
        ]

        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can see all orders")

