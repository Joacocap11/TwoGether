from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserOut, AdminUserCreate
from ..auth import get_current_user, hash_password
router=APIRouter(prefix='/users',tags=['users'])

def admin(user:User=Depends(get_current_user)):
    if not user.is_admin: raise HTTPException(403,'Administrator access required')
    return user

@router.get('/me',response_model=UserOut)
def current(user=Depends(get_current_user)): return user

@router.get('',response_model=list[UserOut])
def users(db:Session=Depends(get_db),_:User=Depends(get_current_user)): return db.query(User).order_by(User.id).all()

@router.post('',response_model=UserOut,status_code=201)
def create_user(data:AdminUserCreate,db:Session=Depends(get_db),_:User=Depends(admin)):
    if db.query(User).filter(User.email==data.email).first(): raise HTTPException(409,'Email already registered')
    user=User(name=data.name,email=data.email,hashed_password=hash_password(data.password),must_change_password=True)
    db.add(user); db.commit(); db.refresh(user); return user

@router.patch('/{user_id}/active',response_model=UserOut)
def set_active(user_id:int,active:bool,db:Session=Depends(get_db),current:User=Depends(admin)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,'User not found')
    if user.id==current.id and not active: raise HTTPException(400,'You cannot deactivate your own account')
    user.is_active=active; db.commit(); db.refresh(user); return user

@router.post('/{user_id}/force-password-change',response_model=UserOut)
def force_password_change(user_id:int,db:Session=Depends(get_db),_:User=Depends(admin)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,'User not found')
    user.must_change_password=True; db.commit(); db.refresh(user); return user
