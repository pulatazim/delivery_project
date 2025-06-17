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
        product_id=order.product_id
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
            "product": {
                "id": new_order.product.id,
                "name": new_order.product.name,
                "price": new_order.product.price,
            },
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_statuses.value,
            "total_price": new_order.quantity * new_order.product.price
        }
    }

    response = data
    return jsonable_encoder(response)


@order_routes.get('/list', status_code=status.HTTP_200_OK)
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
                'product': {
                    "id": order.product.id if order.product else None,
                    "name": order.product.name if order.product else None,
                    "price": order.product.price if order.product else None,
                },
                'quantity': order.quantity,
                'order_statuses': order.order_statuses.value,
                "total_price": order.quantity * order.product.price if order.product else 0
            }
            for order in orders
        ]



        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can see all orders")


@order_routes.get('/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only SuperAdmin can see all orders")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        custom_order = {
            'id': order.id,
            'user': {
                'id': order.user.id,
                'username': order.user.username,
                'email': order.user.email
            },
            'product': {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price,
            },
            'quantity': order.quantity,
            'order_statuses': order.order_statuses.value,
            "total_price": order.quantity * order.product.price
        }

        return jsonable_encoder(custom_order)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin is Allowed to this request")


@order_routes.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    print("username", username)
    user = session.query(User).filter(User.username == username).first()

    custom_data = [
        {
            'id': order.id,
            'user': {
                'id': order.user.id,
                'username': order.user.username,
                'email': order.user.email
            },
            'product': {
                'id': order.product.id,
                'name': order.product.name,
                'price': order.product.price,
            },
            'quantity': order.quantity,
            'order_statuses': order.order_statuses.value,
            'total_price': order.quantity * order.product.price
        }
        for order in user.orders
    ]
    return jsonable_encoder(custom_data)


@order_routes.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_user_by_id(id:int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id, Order.user == current_user).first()
    # orders = current_user.orders

    if order:
        order_data = {
            'id': order.id,
            'user': {
                'id': order.user.id,
                'username': order.user.username,
                'email': order.user.email,
            },
            'product': {
                'id': order.product.id,
                'name': order.product.name,
                'price': order.product.price,
            },
            'quantity': order.quantity,
            'order_statuses': order.order_statuses.value,
            'total_price': order.quantity * order.product.price,
        }
        return jsonable_encoder(order_data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


@order_routes.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()
    order_to_update = session.query(Order).filter(Order.id == id).first()

    if not order_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order_to_update.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, siz boshqalarning buyurtmasini o'zgartira olmaysiz!")

    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "messages": "Sizning buyurtmangiz muvaffaqiyatli o'zgartirlildi!",
        "data": {
            "id": order_to_update.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_statuses": order.order_status
        }
    }
    return jsonable_encoder(custom_response)


@order_routes.patch('/{id}/update-status', status_code=status.HTTP_200_OK)
async def update_or_status(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    if user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()
        order_to_update.order_statuses = order.order_statuses
        session.commit()

        custom_response = {
            "success": True,
            "code": 200,
            "message": "User order is successfully updated!",
            "data": {
                "id": order_to_update.id,
                "order_status": order_to_update.order_statuses
            }
        }
        return jsonable_encoder(custom_response)


@order_routes.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async  def order_delete(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id).first()

    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, boshqalarning orderini o'chira olmaysiz!")

    if order.order_statuses != "PENDING":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz, bu orderni o'chira omaysiz!")

    session.delete(order)
    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "message": "Order deleted successfully!",
        "data": None
    }








