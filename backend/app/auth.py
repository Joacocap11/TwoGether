import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User, RefreshToken

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

# ---------------------------------------------------------
# Refresh tokens: opaque high-entropy secrets, stored hashed
# (never plaintext) so a DB leak doesn't expose usable tokens.
# Rotation: every refresh revokes the token used and issues a
# new one; reuse of an already-revoked token revokes the whole
# session family for that user (theft mitigation).
# ---------------------------------------------------------

def _now(): return datetime.now(timezone.utc).replace(tzinfo=None)
def _hash_refresh_token(raw:str) -> str: return hashlib.sha256(raw.encode()).hexdigest()

def issue_refresh_token(db:Session, user_id:int, user_agent:str|None=None):
    raw=secrets.token_urlsafe(48)
    expires_at=_now()+timedelta(days=settings.refresh_token_expire_days)
    row=RefreshToken(user_id=user_id, token_hash=_hash_refresh_token(raw), expires_at=expires_at, user_agent=user_agent)
    db.add(row); db.flush()
    return raw, expires_at, row

def rotate_refresh_token(db:Session, raw_token:str, user_agent:str|None=None):
    exc=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired refresh token')
    row=db.query(RefreshToken).filter_by(token_hash=_hash_refresh_token(raw_token)).first()
    if not row: raise exc
    now=_now()
    if row.revoked_at is not None:
        # Reuse of a rotated-away token: likely theft. Kill every active
        # session for this user so the legitimate device must log in again.
        db.query(RefreshToken).filter(RefreshToken.user_id==row.user_id, RefreshToken.revoked_at.is_(None)).update({'revoked_at':now})
        db.commit()
        raise exc
    if row.expires_at<now: raise exc
    user=db.get(User,row.user_id)
    if not user or not user.is_active: raise exc
    row.revoked_at=now
    new_raw,new_expires_at,new_row=issue_refresh_token(db,user.id,user_agent)
    row.replaced_by_id=new_row.id
    db.commit()
    return user,new_raw,new_expires_at

def revoke_refresh_token(db:Session, raw_token:str) -> bool:
    row=db.query(RefreshToken).filter_by(token_hash=_hash_refresh_token(raw_token), revoked_at=None).first()
    if not row: return False
    row.revoked_at=_now(); db.commit()
    return True
