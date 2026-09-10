from fastapi import FastAPI,APIRouter, Depends, HTTPException, status
from pydantic import BaseModel,Field
from typing import Annotated,Optional
from model import Users
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from database import engine,SessionLocal
from sqlalchemy.orm import Session 
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt
from datetime import timedelta,datetime,timezone
from router.auth import get_current_user
from model import Todos

# creating this file for making user authentication using database 
# and to connect this file need APIRounter and also taken "router" to connect with main file .
router = APIRouter()

# data base setting:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# configuration to access the data base 
db_dependency = Annotated[Session, Depends(get_db)]

# configuration to access user data from JWT token:
# type of user_dependency is Dictionary
user_dependency = Annotated[dict,Depends(get_current_user)] 



@router.get('/admin/todos')
def read_all_todo(user:user_dependency,db:db_dependency):

    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=404,detail='The user not Found / not authenticated')

    return db.query(Todos).all()



# ---------------------- DELETE Todo from admin role :



@router.delete("/admin/delete/{todo_id}")
def delete_todos_by_admin(user:user_dependency,todo_id :int , db:db_dependency):


    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=404 , detail='No user is logged in !')
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # making query on Todos table to delete the record with the given todo_id and then committing the changes to the database.
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Todo deleted successfully"})



