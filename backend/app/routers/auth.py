from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from ..config import settings
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, Token, PasswordChange, RefreshRequest
from ..auth import (
    hash_password, verify_password, create_access_token, get_current_user,
    issue_refresh_token, rotate_refresh_token, revoke_refresh_token,
)
router=APIRouter(prefix='/auth',tags=['auth'])

# ---------------------------------------------------------
# Client differentiation for the refresh token transport:
# mobile has no cookie jar shared with fetch by default and
# needs the raw refresh token to store in SecureStore, so it
# opts in explicitly via the standard OAuth2 `client_id` form
# field (client_id=mobile). Web never sends that field, so it
# gets the refresh token exclusively as an httpOnly cookie and
# never sees the raw value. This is an explicit, spec-compliant
# signal — not a User-Agent sniff.
# ---------------------------------------------------------
MOBILE_CLIENT_ID='mobile'
COOKIE_PATH='/api/v1/auth'

def _set_refresh_cookie(response:Response, raw_token:str, expires_at):
    max_age=max(int((expires_at-datetime.now(timezone.utc).replace(tzinfo=None)).total_seconds()), 0)
    response.set_cookie(
        key=settings.refresh_cookie_name, value=raw_token, max_age=max_age,
        httponly=True, secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite, path=COOKIE_PATH,
        domain=settings.refresh_cookie_domain,
    )

def _clear_refresh_cookie(response:Response):
    response.delete_cookie(key=settings.refresh_cookie_name, path=COOKIE_PATH, domain=settings.refresh_cookie_domain)

@router.post('/register',response_model=UserOut,status_code=201)
def register(data:UserCreate,db:Session=Depends(get_db)):
    if not settings.registration_enabled: raise HTTPException(403,'Registration is disabled; use the seed command')
    if db.query(User).count() >= 2: raise HTTPException(403,'Registration is disabled for this private application')
    if db.query(User).filter(User.email==data.email).first(): raise HTTPException(409,'Email already registered')
    u=User(name=data.name,email=data.email,hashed_password=hash_password(data.password)); db.add(u); db.commit(); db.refresh(u); return u

@router.post('/login',response_model=Token)
def login(form:OAuth2PasswordRequestForm=Depends(),request:Request=None,response:Response=None,db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==form.username).first()
    if not u or not verify_password(form.password,u.hashed_password): raise HTTPException(401,'Incorrect email or password')
    access=create_access_token(u.id)
    raw_refresh,expires_at,_=issue_refresh_token(db,u.id,request.headers.get('user-agent'))
    db.commit()
    if form.client_id==MOBILE_CLIENT_ID:
        return Token(access_token=access,must_change_password=u.must_change_password,refresh_token=raw_refresh)
    _set_refresh_cookie(response,raw_refresh,expires_at)
    return Token(access_token=access,must_change_password=u.must_change_password)

@router.post('/refresh',response_model=Token)
def refresh(request:Request,response:Response,body:RefreshRequest|None=Body(default=None),db:Session=Depends(get_db)):
    body_token=body.refresh_token if body else None
    cookie_token=request.cookies.get(settings.refresh_cookie_name)
    source_token=body_token or cookie_token
    if not source_token: raise HTTPException(401,'Missing refresh token')
    user,new_raw,new_expires_at=rotate_refresh_token(db,source_token,request.headers.get('user-agent'))
    access=create_access_token(user.id)
    if body_token:
        return Token(access_token=access,must_change_password=user.must_change_password,refresh_token=new_raw)
    _set_refresh_cookie(response,new_raw,new_expires_at)
    return Token(access_token=access,must_change_password=user.must_change_password)

@router.post('/logout',status_code=204)
def logout(request:Request,response:Response,body:RefreshRequest|None=Body(default=None),db:Session=Depends(get_db)):
    body_token=body.refresh_token if body else None
    cookie_token=request.cookies.get(settings.refresh_cookie_name)
    source_token=body_token or cookie_token
    if source_token: revoke_refresh_token(db,source_token)
    if cookie_token: _clear_refresh_cookie(response)

@router.post('/change-password',response_model=UserOut)
def change_password(data:PasswordChange,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if data.new_password != data.confirm_password: raise HTTPException(422,'Passwords do not match')
    if not user.must_change_password and (not data.current_password or not verify_password(data.current_password,user.hashed_password)):
        raise HTTPException(400,'Current password is incorrect')
    user.hashed_password=hash_password(data.new_password); user.must_change_password=False
    db.commit(); db.refresh(user); return user

@router.get('/me',response_model=UserOut)
def me(user=Depends(get_current_user)): return user
