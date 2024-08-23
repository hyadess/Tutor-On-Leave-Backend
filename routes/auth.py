from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal, get_db, db_dependency
from dataStruct.requestModels import UserRequest,logoutRequest,SignupRequest # the user input model
from dataStruct.models import Users  # the database model
from dataStruct.responseModels import TokenResponse  # the response model
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")



@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(user: SignupRequest, db: db_dependency):
    db_user = Users(username=user.username, email=user.email, hashed_password=bcrypt_context.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: UserRequest, db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(user.username, user.id, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


@router.post("/logout")
async def logout(logout:logoutRequest, token: Annotated[str, Depends(oauth2_bearer)]): 
  
    userInfo=verify_user(token)
    if userInfo["username"]!=logout.username:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return {"message": "Successfully logged out."}




#helper functions..........................................

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    to_encode = {"sub": username, "user_id": user_id, "exp": datetime.utcnow() + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise credentials_exception
    
