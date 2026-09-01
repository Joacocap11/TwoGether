from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..db import get_db
from ..models import HotelRating, HotelVisit, MediaEntry, MediaRating, User
from ..schemas import HotelCreate, HotelOut, MediaCreate, MediaOut
from ..uploads import save_upload

router=APIRouter(tags=['media','hotels'])

def _users(db, ratings):
    ids=[r.user_id for r in ratings]
    if len(set(ids)) != 2 or db.query(User).filter(User.id.in_(ids), User.is_active.is_(True)).count()!=2:
        raise HTTPException(422,'Exactly two distinct active users are required')

def media_view(item):
    ratings=item.ratings or []
    return {**{k:getattr(item,k) for k in ('id','title','media_type','watched_date','category','image_path','created_at','updated_at')},'ratings':ratings,'average_rating':sum(r.score for r in ratings)/len(ratings) if ratings else None}

def hotel_view(item):
    ratings=item.ratings or []
    return {**{k:getattr(item,k) for k in ('id','name','visit_date','location','total_price','currency','image_path','created_at','updated_at')},'ratings':ratings,'average_rating':sum(r.score for r in ratings)/len(ratings) if ratings else None}

def save_media_ratings(db,item,ratings):
    _users(db,ratings)
    for data in ratings:
        rating=db.query(MediaRating).filter_by(media_entry_id=item.id,user_id=data.user_id).first()
        if rating is None: rating=MediaRating(media_entry_id=item.id,user_id=data.user_id); db.add(rating)
        rating.score=data.score; rating.opinion=data.opinion
def save_hotel_ratings(db,item,ratings):
    _users(db,ratings)
    for data in ratings:
        rating=db.query(HotelRating).filter_by(hotel_visit_id=item.id,user_id=data.user_id).first()
        if rating is None: rating=HotelRating(hotel_visit_id=item.id,user_id=data.user_id); db.add(rating)
        rating.score=data.score; rating.opinion=data.opinion

@router.get('/media',response_model=list[MediaOut])
def list_media(db:Session=Depends(get_db),_=Depends(get_current_user)): return [media_view(x) for x in db.query(MediaEntry).order_by(MediaEntry.watched_date.desc()).all()]
@router.post('/media',response_model=MediaOut,status_code=201)
def create_media(data:MediaCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=MediaEntry(title=data.title,media_type=data.media_type,watched_date=data.watched_date,category=data.category); db.add(item); db.flush(); save_media_ratings(db,item,data.ratings); db.commit(); db.refresh(item); return media_view(item)
@router.get('/media/{item_id}',response_model=MediaOut)
def get_media(item_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(MediaEntry,item_id)
    if not item: raise HTTPException(404,'Media entry not found')
    return media_view(item)
@router.put('/media/{item_id}',response_model=MediaOut)
def update_media(item_id:int,data:MediaCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(MediaEntry,item_id)
    if not item: raise HTTPException(404,'Media entry not found')
    item.title=data.title; item.media_type=data.media_type; item.watched_date=data.watched_date; item.category=data.category; save_media_ratings(db,item,data.ratings); db.commit(); db.refresh(item); return media_view(item)
@router.delete('/media/{item_id}',status_code=204)
def delete_media(item_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(MediaEntry,item_id)
    if not item: raise HTTPException(404,'Media entry not found')
    db.delete(item); db.commit()
@router.post('/media/{item_id}/upload',response_model=MediaOut)
async def upload_media(item_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(MediaEntry,item_id)
    if not item: raise HTTPException(404,'Media entry not found')
    item.image_path=await save_upload(image); db.commit(); db.refresh(item); return media_view(item)

@router.get('/hotels',response_model=list[HotelOut])
def list_hotels(db:Session=Depends(get_db),_=Depends(get_current_user)): return [hotel_view(x) for x in db.query(HotelVisit).order_by(HotelVisit.visit_date.desc()).all()]
@router.post('/hotels',response_model=HotelOut,status_code=201)
def create_hotel(data:HotelCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=HotelVisit(name=data.name,visit_date=data.visit_date,location=data.location,total_price=data.total_price,currency=data.currency); db.add(item); db.flush(); save_hotel_ratings(db,item,data.ratings); db.commit(); db.refresh(item); return hotel_view(item)
@router.get('/hotels/{item_id}',response_model=HotelOut)
def get_hotel(item_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(HotelVisit,item_id)
    if not item: raise HTTPException(404,'Hotel not found')
    return hotel_view(item)
@router.put('/hotels/{item_id}',response_model=HotelOut)
def update_hotel(item_id:int,data:HotelCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(HotelVisit,item_id)
    if not item: raise HTTPException(404,'Hotel not found')
    item.name=data.name; item.visit_date=data.visit_date; item.location=data.location; item.total_price=data.total_price; item.currency=data.currency; save_hotel_ratings(db,item,data.ratings); db.commit(); db.refresh(item); return hotel_view(item)
@router.delete('/hotels/{item_id}',status_code=204)
def delete_hotel(item_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(HotelVisit,item_id)
    if not item: raise HTTPException(404,'Hotel not found')
    db.delete(item); db.commit()
@router.post('/hotels/{item_id}/upload',response_model=HotelOut)
async def upload_hotel(item_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    item=db.get(HotelVisit,item_id)
    if not item: raise HTTPException(404,'Hotel not found')
    item.image_path=await save_upload(image); db.commit(); db.refresh(item); return hotel_view(item)
