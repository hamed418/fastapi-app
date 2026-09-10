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


# creating this file for making user authentication using database 
# and to connect this file need APIRounter and also taken "router" to connect with main file .
router = APIRouter()



# creates a password hashing configuration using Passlib.
# Use bcrypt as the password hashing algorithm
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto') 


# data base setting:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# configuration to access the data base 
db_dependency = Annotated[Session, Depends(get_db)]

# ------------------------ POST (create user) request -----------------------


# for datavalidation :
# id will automatically created 
class CreateUsers(BaseModel):
    email:str
    username:str
    firstname : str
    lastname: str
    password : str   # we have to hash password and than save into database
    role : str
    phone_number : str

@router.post('/createuser')
def create_user(new_user:CreateUsers,db:db_dependency):
    user_model = Users(
        email=new_user.email,
        username=new_user.username,
        firstname=new_user.firstname,
        lastname = new_user.lastname,
        hash_password=bcrypt_context.hash(new_user.password),
        is_active=True,
        role = new_user.role,
        phone_number = new_user.phone_number

    )

    db.add(user_model)
    db.commit()

    return JSONResponse(status_code=201,content={"message":"user created successfully"})




# ------------------------------- Login --------------------------------
# user access using username and password  ------------
# so POST request have to make 


# to find user if they located in the database .
def authenticate_user(username,password,db):
    user = db.query(Users).filter(Users.username==username).first()
    if user is None:
        return False

    # matching password:
    # decoding hash_password and matching with previous password.
    if bcrypt_context.verify(password,user.hash_password):
        return user # after verify = True we need user info to allocate JWT token to that exact user 
    return False



# ------------------------- JWT (Json Web Token) ------------------------
# IN JWT there are 3 part:
# xxxxx.yyyyy.zzzzz  ==> HEADER.PAYLOAD.SIGNATURE
# payload ==> { "sub": "123", "username": "alvi", "exp": 1756400000 }
# header ==> { "alg": "HS256", "typ": "JWT" }
# Signature ==> signature = HMAC( header + "." + payload, SECRET_KEY )

SECRET_KEY = "2cf2e3a62653aac971cfba4d0039e1f585a9cdde090eb6cec575c9d8b7a6d59b"
ALGORITHM = "HS256"

# this function will generate access token 
def create_access_token(username:str,user_id:int,role: str ,expires_delta:timedelta):
    # creating payload for JWT token 
    encode = {"sub":username,"id":user_id,'role':role}

    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp":expires})
    # Allocating an access token to that user who have just logged in.
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)



# ----------------------- JWT token DECODE --------------------------

# It tells FastAPI: "Get the JWT token from the request."
# because out url is '/login'  so tokenUrl ='login'
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

# extracting username and id from JWT token or decoding jwt to extract username,user_id and role of the user from the jwt token 
def get_current_user(token: Annotated[str,Depends(OAuth2_bearer)]):

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        role=payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=404 , detail='user not found')

        return {'username':username,'id':user_id,'role':role}
    except:
        raise HTTPException(status_code=404,detail='User not Found')





# ----------------------------- login in the system:
@router.post('/login')
def login_user(db:db_dependency, form_data:Annotated[OAuth2PasswordRequestForm, Depends() ]):

    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=401,detail='Invalid username or password/Failed Authentication')
    
    # but if user find than we will allocate an token for the user
    token = create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
    return {'access_token':token,'token_type':'bearer'}   # this token store all information about this user





# ----------------------------- Update user information -----------------------------




user_dependency = Annotated[dict,Depends(get_current_user)]


class Update_User(BaseModel):
    email: Optional[str]=Field(default=None)
    username:Optional[str]=Field(default=None)
    firstname : Optional[str]=Field(default=None)
    lastname: Optional[str]=Field(default=None)
    phone_number : Optional[str]=Field(default=None)



@router.put("/edituser")
def update_user_(user:user_dependency, db : db_dependency,update_user:Update_User):  

    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')
    
    user = db.query(Users).filter(Users.id == user.get('id')).first() 


    # update_todo is a pydantic object that contains the fields to be updated. We will use the model_dump() method to convert it to a dictionary 
    update_data = update_user.model_dump(exclude_unset=True) # here exclude_unset=True is used to exclude the fields that are not set in the request body.

    # setattr() is a built-in function that is used to set the attribute of an object to a new value. It takes three arguments: the object, the name of the attribute, and the new value. 
    # user.email = "updated data" 
    for key, value in update_data.items():
        setattr(user, key, value)  # here setattr() is used to set the attribute of the object to the new value.
    
    db.commit()

    return JSONResponse(status_code=200, content={"message": "User updated successfully"})



# ---------------------------------- update password ---------------------------------

class Update_Password(BaseModel):
    current_password:str
    new_password:str


@router.put("/passwordchange")
def update_password(user:user_dependency, db : db_dependency, update_password:Update_Password):

    if user is None:
        raise HTTPException(status_code=401 , detail='No user found logged in!')
    
    user = db.query(Users).filter(Users.id == user.get('id')).first() 


    if not bcrypt_context.verify(update_password.current_password,user.hash_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # update password
    user.hash_password= bcrypt_context.hash(update_password.new_password)

    db.add(user)
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Password updated successfully"})
