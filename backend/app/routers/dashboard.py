from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from ..models import PlaceVisit,Dish,TestRecord,UserRating
from ..auth import get_current_user
router=APIRouter(prefix='/dashboard',tags=['dashboard'])
@router.get('')
def dashboard(db:Session=Depends(get_db),_=Depends(get_current_user)):
    return {'places':db.query(PlaceVisit).filter(PlaceVisit.deleted_at.is_(None)).count(),'dishes':db.query(Dish).count(),'tests':db.query(TestRecord).count(),'ratings':db.query(UserRating).count(),'average_rating':db.query(func.avg(UserRating.score)).scalar()}
