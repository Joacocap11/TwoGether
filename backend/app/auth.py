from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User

pwd_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')
def hash_password(password): return pwd_context.hash(password)
def verify_password(password, hashed): return pwd_context.verify(password, hashed)
def create_access_token(user_id):
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({'sub':str(user_id),'exp':exp}, settings.secret_key, algorithm='HS256')
def get_current_user(token:str=Depends(oauth2_scheme), db:Session=Depends(get_db)):
    exc=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication credentials', headers={'WWW-Authenticate':'Bearer'})
    try:
        payload=jwt.decode(token,settings.secret_key,algorithms=['HS256']); uid=int(payload.get('sub'))
    except (JWTError, TypeError, ValueError): raise exc
    user=db.get(User,uid)
    if not user or not user.is_active: raise exc
    return user
