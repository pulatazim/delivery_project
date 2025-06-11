import datetime
from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from schemas import SignUpModel, LoginModel
from database import engine, session
from models import User

auth_routes = APIRouter(
    prefix="/auth",
)

session = session(bind=engine)


@auth_routes.get("/")
async def welcome(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"message": "Auth Sign up sahifasi"}


@auth_routes.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    data = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff,
    )

    session.add(data)
    session.commit()        # amalga oshirish
    response_model = {
        'success': True,
        'code': 201,
        'message': 'User created successfully',
        'data': {
            'username': user.username,
            'email': user.email,
            'password': generate_password_hash(user.password),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
        }
    }

    return response_model


@auth_routes.post('/login/', status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT=Depends()):

    # db_user = session.query(User).filter(User.username == user.username).first()

    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()
    print('user', db_user)

    if db_user and check_password_hash(db_user.password, user.password):
        access_lifetime = datetime.timedelta(minutes=60)
        refresh_lifetime = datetime.timedelta(days=3)
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)

        token = {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

        response = {
            'success': True,
            'code': 200,
            'message': 'Login successful',
            'data': token
        }

        return jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")


@auth_routes.get('/login/refresh')
async def refresh_token(Authorize: AuthJWT = Depends()):

    try:
        access_lifetime = datetime.timedelta(minutes=60)
        refresh_lifetime = datetime.timedelta(days=7)
        Authorize.jwt_refresh_token_required()              # valit access tokinni so'raydi
        current_user = Authorize.get_jwt_subject()          # access tokendan usernameni ajratib oladi

        db_user = session.query(User).filter(User.username == current_user).first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # access token yaratamiz
        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)

        response_model = {
            'success': True,
            'code': 200,
            'message': 'New access token created',
            'data': {
                'access_token': new_access_token,
            }
        }

        return response_model

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
