from database import engine, Base
from models import Product, User, Order


Base.metadata.create_all(engine)
