from fastapi import APIRouter, Depends, HTTPException
from ..config import settings
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, Token, PasswordChange
from ..auth import hash_password, verify_password, create_access_token, get_current_user
router=APIRouter(prefix='/auth',tags=['auth'])
@router.post('/register',response_model=UserOut,status_code=201)
def register(data:UserCreate,db:Session=Depends(get_db)):
    if not settings.registration_enabled: raise HTTPException(403,'Registration is disabled; use the seed command')
    if db.query(User).count() >= 2: raise HTTPException(403,'Registration is disabled for this private application')
    if db.query(User).filter(User.email==data.email).first(): raise HTTPException(409,'Email already registered')
    u=User(name=data.name,email=data.email,hashed_password=hash_password(data.password)); db.add(u); db.commit(); db.refresh(u); return u
@router.post('/login',response_model=Token)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==form.username).first()
    if not u or not verify_password(form.password,u.hashed_password): raise HTTPException(401,'Incorrect email or password')
    return Token(access_token=create_access_token(u.id),must_change_password=u.must_change_password)
@router.post('/change-password',response_model=UserOut)
def change_password(data:PasswordChange,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if data.new_password != data.confirm_password: raise HTTPException(422,'Passwords do not match')
    if not user.must_change_password and (not data.current_password or not verify_password(data.current_password,user.hashed_password)):
        raise HTTPException(400,'Current password is incorrect')
    user.hashed_password=hash_password(data.new_password); user.must_change_password=False
    db.commit(); db.refresh(user); return user
@router.get('/me',response_model=UserOut)
def me(user=Depends(get_current_user)): return user
