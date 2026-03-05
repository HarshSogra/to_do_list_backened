from sqlalchemy import Column, Integer,String,Boolean
from database import Base

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    deadline = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
