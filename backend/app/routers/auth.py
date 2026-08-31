from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, Token
from ..auth import hash_password, verify_password, create_access_token, get_current_user
router=APIRouter(prefix='/auth',tags=['auth'])
@router.post('/register',response_model=UserOut,status_code=201)
def register(data:UserCreate,db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first(): raise HTTPException(409,'Email already registered')
    u=User(name=data.name,email=data.email,hashed_password=hash_password(data.password)); db.add(u); db.commit(); db.refresh(u); return u
@router.post('/login',response_model=Token)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==form.username).first()
    if not u or not verify_password(form.password,u.hashed_password): raise HTTPException(401,'Incorrect email or password')
    return Token(access_token=create_access_token(u.id))
@router.get('/me',response_model=UserOut)
def me(user=Depends(get_current_user)): return user
