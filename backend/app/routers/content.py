from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Dish, PlaceVisit, TestRecord
from ..schemas import DishCreate,DishOut,TestCreate,TestOut
from ..auth import get_current_user
from ..uploads import save_upload
router=APIRouter(tags=['dishes','tests'])
@router.get('/dishes',response_model=list[DishOut])
def dishes(db:Session=Depends(get_db),_=Depends(get_current_user)): return db.query(Dish).all()
@router.post('/dishes',response_model=DishOut,status_code=201)
def add_dish(data:DishCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    if not db.query(PlaceVisit).filter(PlaceVisit.id==data.visit_id,PlaceVisit.deleted_at.is_(None)).first(): raise HTTPException(404,'Place not found')
    d=Dish(**data.model_dump()); db.add(d); db.commit(); db.refresh(d); return d
@router.post('/dishes/{dish_id}/upload',response_model=DishOut)
async def dish_upload(dish_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    d=db.get(Dish,dish_id)
    if not d: raise HTTPException(404,'Dish not found')
    d.image_path=await save_upload(image); db.commit(); db.refresh(d); return d
@router.get('/tests',response_model=list[TestOut])
def tests(db:Session=Depends(get_db),_=Depends(get_current_user)): return db.query(TestRecord).order_by(TestRecord.test_date.desc()).all()
@router.post('/tests',response_model=TestOut,status_code=201)
def add_test(data:TestCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    t=TestRecord(**data.model_dump()); db.add(t); db.commit(); db.refresh(t); return t
@router.put('/tests/{test_id}',response_model=TestOut)
def update_test(test_id:int,data:TestCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    t=db.get(TestRecord,test_id)
    if not t: raise HTTPException(404,'Test not found')
    for key,value in data.model_dump().items(): setattr(t,key,value)
    db.commit(); db.refresh(t); return t
@router.delete('/tests/{test_id}',status_code=204)
def delete_test(test_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    t=db.get(TestRecord,test_id)
    if not t: raise HTTPException(404,'Test not found')
    db.delete(t); db.commit()
@router.post('/tests/{test_id}/upload',response_model=TestOut)
async def test_upload(test_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    t=db.get(TestRecord,test_id)
    if not t: raise HTTPException(404,'Test not found')
    t.image_path=await save_upload(image); db.commit(); db.refresh(t); return t
