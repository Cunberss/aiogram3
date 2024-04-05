from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey
from src.db.base import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(String, default='Unknown')


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    photo_url = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)


class SubCategory(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    category_id = Column(Integer, ForeignKey('categories.id'))


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))


class CartItem(Base):
    __tablename__ = 'cartsitems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
