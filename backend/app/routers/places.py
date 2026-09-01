from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import PlaceVisit, UserRating, Dish, User
from ..schemas import PlaceCreate, PlaceOut, PlaceDetail, RatingCreate, RatingOut, PlaceComplete
from ..auth import get_current_user
from ..uploads import save_upload
router=APIRouter(prefix='/places',tags=['places'])

def view(p, detail=False):
    place_average=sum(r.score for r in p.ratings)/len(p.ratings) if p.ratings else None
    dish_average=sum(d.score for d in p.dishes)/len(p.dishes) if p.dishes else None
    photos=[p.image_path] if p.image_path else []
    photos.extend(d.image_path for d in p.dishes if d.image_path)
    result={**{k:getattr(p,k) for k in ('id','name','visit_date','location','notes','category','image_path','created_at','updated_at')},
            'average_rating':place_average, 'place_average_rating':place_average,
            'dish_average_rating':dish_average, 'photos':photos}
    if detail: result.update(ratings=p.ratings, dishes=p.dishes)
    return result

def _users(db, entries):
    ids=[e.user_id for e in entries]
    if len(set(ids)) != 2: raise HTTPException(422,'Exactly two distinct users are required')
    users=db.query(User).filter(User.id.in_(ids), User.is_active.is_(True)).all()
    if len(users)!=2: raise HTTPException(422,'Both users must be active')

def _save_entries(db, place, entries):
    _users(db, entries)
    for entry in entries:
        rating=db.query(UserRating).filter_by(visit_id=place.id,user_id=entry.user_id).first()
        if rating is None: rating=UserRating(visit_id=place.id,user_id=entry.user_id); db.add(rating)
        rating.score=entry.rating.score; rating.comment=entry.rating.comment
        dish=db.query(Dish).filter_by(visit_id=place.id,user_id=entry.user_id).first()
        if dish is None: dish=Dish(visit_id=place.id,user_id=entry.user_id); db.add(dish)
        for key,value in entry.dish.model_dump().items(): setattr(dish,key,value)

@router.get('',response_model=list[PlaceOut])
def list_places(db:Session=Depends(get_db),_=Depends(get_current_user)):
    return [view(p,True) for p in db.query(PlaceVisit).filter(PlaceVisit.deleted_at.is_(None)).order_by(PlaceVisit.visit_date.desc()).all()]
@router.post('',response_model=PlaceOut,status_code=201)
def create_place(data:PlaceCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=PlaceVisit(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return view(p)
@router.post('/complete',response_model=PlaceDetail,status_code=201)
def create_complete(data:PlaceComplete,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=PlaceVisit(**data.place.model_dump()); db.add(p); db.flush(); _save_entries(db,p,data.entries); db.commit(); db.refresh(p); return view(p,True)
@router.put('/{place_id}/complete',response_model=PlaceDetail)
def update_complete(place_id:int,data:PlaceComplete,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    for key,value in data.place.model_dump().items(): setattr(p,key,value)
    _save_entries(db,p,data.entries); db.commit(); db.refresh(p); return view(p,True)
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
@router.get('/{place_id}',response_model=PlaceDetail)
def get_place(place_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    p=db.query(PlaceVisit).filter(PlaceVisit.id==place_id,PlaceVisit.deleted_at.is_(None)).first()
    if not p: raise HTTPException(404,'Place not found')
    return view(p,True)
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
