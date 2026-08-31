from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Dish, PlaceVisit, TestRecord, TestOutcome, User
from ..schemas import DishCreate,DishOut,TestCreate,TestOut,TestComplete
from ..auth import get_current_user
from ..uploads import save_upload
router=APIRouter(tags=['dishes','tests'])
@router.get('/dishes',response_model=list[DishOut])
def dishes(db:Session=Depends(get_db),_=Depends(get_current_user)): return db.query(Dish).all()
@router.post('/dishes',response_model=DishOut,status_code=201)
def add_dish(data:DishCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    if not db.query(PlaceVisit).filter(PlaceVisit.id==data.visit_id,PlaceVisit.deleted_at.is_(None)).first(): raise HTTPException(404,'Place not found')
    d=Dish(**data.model_dump()); db.add(d); db.commit(); db.refresh(d); return d
@router.put('/dishes/{dish_id}',response_model=DishOut)
def update_dish(dish_id:int,data:DishCreate,db:Session=Depends(get_db),_=Depends(get_current_user)):
    d=db.get(Dish,dish_id)
    if not d: raise HTTPException(404,'Dish not found')
    for key,value in data.model_dump().items(): setattr(d,key,value)
    db.commit(); db.refresh(d); return d
@router.delete('/dishes/{dish_id}',status_code=204)
def delete_dish(dish_id:int,db:Session=Depends(get_db),_=Depends(get_current_user)):
    d=db.get(Dish,dish_id)
    if not d: raise HTTPException(404,'Dish not found')
    db.delete(d); db.commit()
@router.post('/dishes/{dish_id}/upload',response_model=DishOut)
async def dish_upload(dish_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    d=db.get(Dish,dish_id)
    if not d: raise HTTPException(404,'Dish not found')
    d.image_path=await save_upload(image); db.commit(); db.refresh(d); return d

def _validate_outcomes(db, outcomes):
    ids=[o.user_id for o in outcomes]
    if len(set(ids)) != 2: raise HTTPException(422,'Exactly two distinct users are required')
    if db.query(User).filter(User.id.in_(ids),User.is_active.is_(True)).count()!=2: raise HTTPException(422,'Both users must be active')

def _save_outcomes(db,t,data):
    _validate_outcomes(db,data)
    for item in data:
        outcome=db.query(TestOutcome).filter_by(test_record_id=t.id,user_id=item.user_id).first()
        if outcome is None: outcome=TestOutcome(test_record_id=t.id,user_id=item.user_id); db.add(outcome)
        outcome.result=item.result

@router.get('/tests',response_model=list[TestOut])
def tests(db:Session=Depends(get_db),_=Depends(get_current_user)): return db.query(TestRecord).order_by(TestRecord.test_date.desc()).all()
@router.post('/tests/complete',response_model=TestOut,status_code=201)
def add_complete_test(data:TestComplete,db:Session=Depends(get_db),_=Depends(get_current_user)):
    t=TestRecord(title=data.title,result='; '.join(o.result for o in data.outcomes),test_date=data.test_date,notes=data.notes)
    db.add(t); db.flush(); _save_outcomes(db,t,data.outcomes); db.commit(); db.refresh(t); return t
@router.put('/tests/{test_id}/complete',response_model=TestOut)
def update_complete_test(test_id:int,data:TestComplete,db:Session=Depends(get_db),_=Depends(get_current_user)):
    t=db.get(TestRecord,test_id)
    if not t: raise HTTPException(404,'Test not found')
    t.title=data.title; t.test_date=data.test_date; t.notes=data.notes; t.result='; '.join(o.result for o in data.outcomes)
    _save_outcomes(db,t,data.outcomes); db.commit(); db.refresh(t); return t
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
@router.post('/tests/{test_id}/outcomes/{outcome_id}/upload',response_model=TestOut)
async def outcome_upload(test_id:int,outcome_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    outcome=db.query(TestOutcome).filter_by(id=outcome_id,test_record_id=test_id).first()
    if not outcome: raise HTTPException(404,'Outcome not found')
    outcome.image_path=await save_upload(image); db.commit(); db.refresh(outcome.test_record); return outcome.test_record
@router.post('/tests/outcomes/{outcome_id}/upload',response_model=TestOut)
async def outcome_upload_direct(outcome_id:int,image:UploadFile=File(...),db:Session=Depends(get_db),_=Depends(get_current_user)):
    outcome=db.get(TestOutcome,outcome_id)
    if not outcome: raise HTTPException(404,'Outcome not found')
    outcome.image_path=await save_upload(image); db.commit(); db.refresh(outcome.test_record); return outcome.test_record
