from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(70), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    order = relationship('Order', back_populates='user')

    def __repr__(self):
        return f"<user {self.username}>"


class Order(Base):
    ORDER_STATUS = (
        ("PENDING", "Pending"),
        ('IN_TRANSIT', "In Transit"),
        ('DELIVERED', "Delivered"),
    )

    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_statuses = Column(ChoiceType(choices=ORDER_STATUS), default='PENDING')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='order')
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='order')

    def __repr__(self):
        return f"<order {self.id}>"


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    order = relationship('Order', back_populates='product')
    price = Column(Integer)

    def __repr__(self):
        return f"<product {self.name}>"



