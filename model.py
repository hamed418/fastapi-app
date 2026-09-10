# ~~~~~~~~~~~~~~ database table create korar jonno model.py file e class create kora hoy ~~~~~~~~~~~~~~

from database import Base 
from sqlalchemy import Column, Integer, String, Boolean,ForeignKey

class Todos(Base):

    __tablename__ = "todos"  # table name

    # Database table has created:
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description=Column(String)
    priority= Column(Integer)
    completed = Column(Boolean,default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))




# ---------------------- user table --------------------------
class Users(Base):

    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True) # index =True means is new user added than auto unique index will generated. 
    email = Column(String,unique=True)
    username=Column(String,unique=True)
    firstname=Column(String)
    lastname=Column(String)
    hash_password=Column(String)
    is_active=Column(Boolean,default=True)
    role = Column(String)
    phone_number = Column(String,nullable=True)  # here we are adding a new column 'phone_number' in the 'users' table. The column is of type String and it is nullable.