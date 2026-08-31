from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from ..models import PlaceVisit, UserRating
from ..schemas import PlaceCreate, PlaceOut, RatingCreate, RatingOut
from ..auth import get_current_user
from ..uploads import save_upload
router=APIRouter(prefix='/places',tags=['places'])
def view(p):
    avg=sum(r.score for r in p.ratings)/len(p.ratings) if p.ratings else None
    return {**{k:getattr(p,k) for k in ('id','name','visit_date','location','notes','image_path','created_at','updated_at')},'average_rating':avg}
@router.get('',response_model=list[PlaceOut])
def list_places(db:Session=Depends(get_db),_=Depends(get_current_user)):
    return [view(p) for p in db.query(PlaceVisit).filter(PlaceVisit.deleted_at.is_(None)).order_by(PlaceVisit.visit_date.desc()).all()]
@router.post('',response_model=PlaceOut,status_code=201)
def create_place(data:PlaceCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=PlaceVisit(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return view(p)
@router.put('/{place_id}',response_model=PlaceOut)
def update_place(place_id:int,data:PlaceCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    for key,value in data.model_dump().items(): setattr(p,key,value)
    db.commit(); db.refresh(p); return view(p)
@router.post('/{place_id}/upload',response_model=PlaceOut)
async def upload_place(place_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    p.image_path=await save_upload(image); db.commit(); db.refresh(p); return view(p)
@router.get('/{place_id}',response_model=PlaceOut)
def get_place(place_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    return view(p)
@router.delete('/{place_id}',status_code=204)
def delete_place(place_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    p.deleted_at=datetime.now(timezone.utc); db.commit()
@router.post('/{place_id}/ratings',response_model=RatingOut,status_code=201)
def rate(place_id:int,data:RatingCreate,db:Session=Depends(get_db),user=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    if db.query(UserRating).filter_by(visit_id=place_id,user_id=user.id).first(): raise HTTPException(409,'You already rated this place')
    r=UserRating(**data.model_dump(),visit_id=place_id,user_id=user.id); db.add(r); db.commit(); db.refresh(r); return r
@router.get('/{place_id}/ratings',response_model=list[RatingOut])
def ratings(place_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    return db.query(UserRating).filter_by(visit_id=place_id).all()
