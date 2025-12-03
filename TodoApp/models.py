from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from TodoApp.database import Base

class Users(Base):
    __tablename__="users"

    id= Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True)
    username=Column(String,unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password=Column(String)
    role=Column(String)
    is_active=Column(Boolean,default=True)
    phone_number=Column(String,unique=True)
 


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer,ForeignKey("users.id"))
