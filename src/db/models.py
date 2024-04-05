from sqlalchemy import Column, Integer, String, BigInteger
from src.db.base import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(String, default='Unknown')
