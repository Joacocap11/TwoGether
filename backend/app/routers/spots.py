from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Spot, SpotRating, SpotStatus, SpotCategory
from ..schemas import SpotCreate, SpotUpdate, SpotOut, SpotRatingCreate, SpotRatingUpdate, SpotRatingOut
from ..auth import get_current_user
from ..uploads import save_upload
router=APIRouter(prefix='/spots',tags=['spots'])

# Design decision: a Spot's ratings are only ever created/shown while
# Spot.status == 'visited'. Moving a visited Spot back to 'wishlist' does NOT
# delete its SpotRating rows -- view() simply omits them from the response
# (and the average) while wishlist, so the opinions aren't lost if the spot
# is marked visited again later.

def view(s):
    visible=s.ratings if s.status==SpotStatus.VISITED else []
    average=sum(r.score for r in visible)/len(visible) if visible else None
    return {**{k:getattr(s,k) for k in ('id','name','location','description','category','visit_date','notes','status','image_path','created_at','updated_at')},
            'ratings':visible,'average_rating':average}
# visit_date is only meaningful once a Spot has actually been visited: it is
# unconditionally cleared server-side whenever status is 'wishlist' (both on
# create and on update), regardless of what the client sends, so a spot that
# goes visited -> wishlist -> visited always starts that new visit with a
# blank date unless the user picks one again.
def _normalize(fields):
    if fields['status']==SpotStatus.WISHLIST: fields['visit_date']=None
    return fields


@router.get('',response_model=list[SpotOut])
def list_spots(status:SpotStatus|None=None,category:SpotCategory|None=None,db:Session=Depends(get_db),_=Depends(get_current_user)):
    q=db.query(Spot)
    if status is not None: q=q.filter(Spot.status==status)
    if category is not None: q=q.filter(Spot.category==category)
    return [view(s) for s in q.order_by(Spot.created_at.desc()).all()]
@router.post('',response_model=SpotOut,status_code=201)
def create_spot(data:SpotCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    s=Spot(**_normalize(data.model_dump())); db.add(s); db.commit(); db.refresh(s); return view(s)
@router.get('/{spot_id}',response_model=SpotOut)
def get_spot(spot_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    return view(s)
@router.put('/{spot_id}',response_model=SpotOut)
def update_spot(spot_id:int,data:SpotUpdate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    for key,value in _normalize(data.model_dump()).items(): setattr(s,key,value)
    db.commit(); db.refresh(s); return view(s)
@router.delete('/{spot_id}',status_code=204)
def delete_spot(spot_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    db.delete(s); db.commit()
@router.post('/{spot_id}/upload',response_model=SpotOut)
async def upload_spot(spot_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    s.image_path=await save_upload(image); db.commit(); db.refresh(s); return view(s)

@router.get('/{spot_id}/ratings',response_model=list[SpotRatingOut])
def list_spot_ratings(spot_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    return s.ratings if s.status==SpotStatus.VISITED else []
@router.post('/{spot_id}/ratings',response_model=SpotRatingOut,status_code=201)
def create_spot_rating(spot_id:int,data:SpotRatingCreate,db:Session=Depends(get_db),user=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    if s.status!=SpotStatus.VISITED: raise HTTPException(409,'Spot must be visited before it can be rated')
    if db.query(SpotRating).filter_by(spot_id=spot_id,user_id=user.id).first():
        raise HTTPException(409,'You already rated this spot; use PUT /spots/{spot_id}/ratings/me to edit it')
    r=SpotRating(**data.model_dump(),spot_id=spot_id,user_id=user.id); db.add(r); db.commit(); db.refresh(r); return r
@router.put('/{spot_id}/ratings/me',response_model=SpotRatingOut)
def update_own_spot_rating(spot_id:int,data:SpotRatingUpdate,db:Session=Depends(get_db),user=Depends(get_current_user)):
    s=db.get(Spot,spot_id)
    if not s: raise HTTPException(404,'Spot not found')
    if s.status!=SpotStatus.VISITED: raise HTTPException(409,'Spot must be visited before it can be rated')
    r=db.query(SpotRating).filter_by(spot_id=spot_id,user_id=user.id).first()
    if not r: raise HTTPException(404,'You have not rated this spot yet; use POST /spots/{spot_id}/ratings to create it')
    r.score=data.score; r.comment=data.comment; db.commit(); db.refresh(r); return r
