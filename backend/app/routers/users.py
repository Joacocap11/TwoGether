from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserOut
from ..auth import get_current_user
router=APIRouter(prefix='/users',tags=['users'])
@router.get('/me',response_model=UserOut)
def current(user=Depends(get_current_user)): return user
@router.get('',response_model=list[UserOut])
def users(db:Session=Depends(get_db),_=Depends(get_current_user)): return db.query(User).filter(User.is_active.is_(True)).all()
