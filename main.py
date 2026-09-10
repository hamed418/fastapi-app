from http.client import HTTPException

from fastapi import FastAPI,Depends
from fastapi.responses import JSONResponse
import model
from model import Todos,Users
from database import engine,SessionLocal
from typing import Annotated,Optional
from sqlalchemy.orm import Session 
from pydantic import BaseModel,Field
from router.auth import  get_current_user  # use to decode token.


# ----------------------------- performing Database CRUD operation according to user access -------------------------------- 

from router import auth
from router import admin
app = FastAPI()

model.Base.metadata.create_all(bind=engine)

# to connect auth file with main app:
app.include_router(auth.router)  # here auth.router is used to include the router from the auth.py file in the main app. It is used to connect the auth.py file with the main app.
app.include_router(admin.router)




# ----------------------------- Database CRUD operation using FastAPI and SQLAlchemy ---------------------------------







# ------------------------------ GET(view database) request in SQLite Database---------------------------------


# To view the data from databse
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# configuration to access the data base
# type of db_dependency is Session because it is a database. 
db_dependency = Annotated[Session, Depends(get_db)]  # here session is used to create a temporary working area through which your application interacts with the database.


# configuration to access user data from JWT token:
# type of user_dependency is Dictionary
user_dependency = Annotated[dict,Depends(get_current_user)] 


@app.get("/")
def read_todos(user:user_dependency, db : db_dependency):   # here session is used to create a temporary working area through which your application interacts with the database.

    # If user is logges in only than the todo belong to use will show!
    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')
    
    # here Todos is the class name of model.py file and db.query() is used to query the database table and .all() is used to fetch all the records from the table.
    # todo will extrated only according to the user.
    return db.query(model.Todos).filter(Todos.owner_id==user.get('id')).all()



# ---------------- get data by id --------------------------

@app.get("/todo/{todo_id}")
def read_specific_todos(user:user_dependency,todo_id: int, db : db_dependency):   # here session is used to create a temporary working area through which your application interacts with the database.

    # it check if user is logged in or not to see the exact todo of the user.
    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')

    
    # here Todos is the class name of model.py file and db.query() is used to query the database table and .all() is used to fetch all the records from the table.
    specific_todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first() # here first() is used to fetch the first record from the table that matches the filter condition.
    if specific_todo is not None:
        return specific_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")



# ------------------------------ POST(insert data) request in SQLite Database(with User Authorization)---------------------------------

# data validation using pydantic BaseModel class
class Todo(BaseModel):
    id: int
    title: str
    description: str= Field(max_length=150)  # here max_length=150 is used to validate the description field to be maximum 150 characters.
    priority: int = Field(gt=1, lt=6)  # here ge=1 and le=5 is used to validate the priority field to be between 1 and 5.
    completed: bool = Field(default=False)





# now create todo in databse only if any user is logged in other wise can't create any todo 
@app.post("/create")
def create_todo(user:user_dependency ,todo:Todo,db :db_dependency):  # here session is used to create a temporary working area through which your application interacts with the database.

    # if no token found to decode beacuse no user is logged in than this bellow line of code will execute.
    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')

    # owner_id is inside user dictionary.which get by decoding token of that exact user.
    todo_model = Todos(**todo.model_dump(),owner_id=user.get('id')) # here **todo.model_dump() is used to convert the pydantic model to a dictionary and then unpack it to the Todos class.

    db.add(todo_model)
    db.commit()

    return JSONResponse(status_code=201, content={"message": "Todo created successfully"})




# --------------------------- PUT(upadate data) request -----------------------------


# for data validation defining another pydantic class 
# we will not take id because id will be in the url for update
class Todo_Update(BaseModel):
    title:Optional[str] =Field(default=None)
    description:Optional[str]=  Field(default=None,max_length=100)
    priority :Optional[int] = Field(default=None,gt=0,lt=6)
    completed:Optional[bool] = Field(default=None)




@app.put("/todo/{todo_id}")
def update_todo(user:user_dependency,todo_id: int, db : db_dependency,update_todo:Todo_Update):  

    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')
    
    todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first() 

    if todo is  None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # update_todo is a pydantic object that contains the fields to be updated. We will use the model_dump() method to convert it to a dictionary 
    update_data = update_todo.model_dump(exclude_unset=True) # here exclude_unset=True is used to exclude the fields that are not set in the request body.

    # setattr() is a built-in function that is used to set the attribute of an object to a new value. It takes three arguments: the object, the name of the attribute, and the new value. 
    # todo.description = "updated data" 
    for key, value in update_data.items():
        setattr(todo, key, value)  # here setattr() is used to set the attribute of the object to the new value.
    
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Todo updated successfully"})




# --------------------- DELETE(delete data) request -----------------------------


@app.delete("/delete/{todo_id}")
def delete_todos(user:user_dependency,todo_id :int , db:db_dependency):


    if user is None:
        raise HTTPException(status_code=404 , detail='No user is logged in !')
    
    todo = db.query(Todos).filter(Todos.owner_id==user.get('id')).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # making query on Todos table to delete the record with the given todo_id and then committing the changes to the database.
    db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).delete()
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Todo deleted successfully"})



# --------------------- GET request to view authenticated users in database (only for admin) -----------------------------

@app.get("/user")
def get_users(user:user_dependency, db : db_dependency):   # here session is used to create a temporary working area through which your application interacts with the database.

    # If user is logges in only than the todo belong to use will show!
    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')
    
    # here Todos is the class name of model.py file and db.query() is used to query the database table and .all() is used to fetch all the records from the table.
    # todo will extrated only according to the user.
    return db.query(Users).filter(Users.id == user.get('id')).first()

