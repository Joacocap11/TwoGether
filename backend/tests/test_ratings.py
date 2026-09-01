import os
from decimal import Decimal
os.environ['DATABASE_URL']='sqlite:///./test_twogether.db'
os.environ['TESTING']='true'
os.environ['REGISTRATION_ENABLED']='true'
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base,engine,SessionLocal
from app.models import Dish, User
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
client=TestClient(app)
def token(email):
    client.post('/api/v1/auth/register',json={'name':email,'email':email,'password':'password123'})
    return client.post('/api/v1/auth/login',data={'username':email,'password':'password123'}).json()['access_token']
def test_rating_rules_and_average():
    joaco=token('a@example.com'); h={'Authorization':f'Bearer {joaco}'}
    p=client.post('/api/v1/places',json={'name':'Cafe','visit_date':'2025-01-01','location':'Madrid','category':'lunch','currency':'UYU'},headers=h).json()
    assert p['currency']=='UYU'
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':0},headers=h).status_code==422
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':11},headers=h).status_code==422
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':5},headers=h).status_code==201
    selena=token('b@example.com'); h2={'Authorization':f'Bearer {selena}'}
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':8},headers=h2).status_code==201
    assert client.post('/api/v1/dishes',json={'name':'Soup','visit_id':p['id'],'user_id':1,'score':4,'dish_price':'450.25','drink_price':'120.00'},headers=h).status_code==201
    assert client.post('/api/v1/dishes',json={'name':'Pasta','visit_id':p['id'],'user_id':2,'score':8,'dish_price':'500.50','dessert_price':'210.75'},headers=h2).status_code==201
    with SessionLocal() as db:
        dishes=db.query(Dish).filter_by(visit_id=p['id']).order_by(Dish.id).all()
        assert dishes[0].dish_price == Decimal('450.25') and dishes[0].drink_price == Decimal('120.00')
        assert dishes[0].dessert_price is None and dishes[1].dessert_price == Decimal('210.75')
    detail=client.get(f"/api/v1/places/{p['id']}",headers=h).json()
    assert detail['place_average_rating']==6.5
    assert detail['dish_average_rating']==6
    assert len(detail['ratings'])==2 and len(detail['dishes'])==2
    assert len(detail['photos'])==0
    test=client.post('/api/v1/tests/complete',json={'title':'Check','test_date':'2025-01-02','outcomes':[{'user_id':1},{'user_id':2}]},headers=h)
    assert test.status_code==201
    assert test.json()['result'] is None
    complete=client.post('/api/v1/places/complete',json={'place':{'name':'Dinner','visit_date':'2025-01-03','category':'dinner','currency':'USD'},'entries':[{'user_id':1,'dish':{'name':'A','score':6,'dish_price':'10.10','drink_price':'2.20','dessert_price':'3.30'},'rating':{'score':7,'comment':'ok'}},{'user_id':2,'dish':{'name':'B','score':8,'dish_price':'11.11'},'rating':{'score':9,'comment':'great'}}]},headers=h).json()
    place_id=complete['id']
    assert client.put(f'/api/v1/places/{place_id}/complete',json={'place':{'name':'Dinner edited','visit_date':'2025-01-04','location':'Madrid','category':'snack','currency':'USD'},'entries':[{'user_id':1,'dish':{'name':'A2','score':7,'dish_price':'12.12'},'rating':{'score':8,'comment':'updated'}},{'user_id':2,'dish':{'name':'B2','score':9,'dish_price':'13.13'},'rating':{'score':10,'comment':'updated'}}]},headers=h).status_code==200
    updated=client.get(f'/api/v1/places/{place_id}',headers=h).json()
    assert updated['id']==place_id and updated['name']=='Dinner edited'
    assert {d['name'] for d in updated['dishes']}=={'A2','B2'} and updated['currency']=='USD'
    assert client.post(f'/api/v1/places/{place_id}/upload',files={'image':('general.png',b'general','image/png')},headers=h).status_code==200
    for dish in updated['dishes']:
        assert client.post(f"/api/v1/dishes/{dish['id']}/upload",files={'image':(f"{dish['id']}.png",b'dish','image/png')},headers=h).status_code==200
    test_id=test.json()['id']
    assert client.put(f'/api/v1/tests/{test_id}',json={'title':'wrong route'},headers=h).status_code==422
    assert client.put(f'/api/v1/tests/{test_id}/complete',json={'title':'Check edited','test_date':'2025-01-05','outcomes':[{'user_id':1},{'user_id':2}]},headers=h).status_code==200
    test_after=client.get('/api/v1/tests',headers=h).json()
    assert len([item for item in test_after if item['id']==test_id])==1
    assert all(outcome['result'] is None for outcome in test.json()['outcomes'])

def test_media_and_hotels_crud():
    login=client.post('/api/v1/auth/login',data={'username':'a@example.com','password':'password123'})
    assert login.status_code==200
    h={'Authorization':f"Bearer {login.json()['access_token']}"}
    media=client.post('/api/v1/media',json={'title':'The Film','media_type':'movie','watched_date':'2025-02-01','category':'Terror','ratings':[{'user_id':1,'score':8,'opinion':'Muy buena fotografía'},{'user_id':2,'score':9,'opinion':'La volvería a ver'}]},headers=h)
    assert media.status_code==201 and media.json()['average_rating']==8.5
    assert {r['opinion'] for r in media.json()['ratings']}=={'Muy buena fotografía','La volvería a ver'}
    media_id=media.json()['id']
    edited=client.put(f'/api/v1/media/{media_id}',json={'title':'The Series','media_type':'series','watched_date':'2025-02-02','category':None,'ratings':[{'user_id':1,'score':7,'opinion':'Actualizada'},{'user_id':2,'score':8,'opinion':None}]},headers=h)
    assert edited.status_code==200 and edited.json()['id']==media_id and edited.json()['media_type']=='series'
    assert {r['opinion'] for r in edited.json()['ratings']}=={'Actualizada',None}
    assert client.delete(f'/api/v1/media/{media_id}',headers=h).status_code==204
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Central','visit_date':'2025-02-03','location':'Madrid','total_price':'2500.75','currency':'USD','ratings':[{'user_id':1,'score':6,'opinion':'Bien'},{'user_id':2,'score':10,'opinion':'Excelente'}]},headers=h)
    assert hotel.status_code==201 and hotel.json()['average_rating']==8 and hotel.json()['total_price']=='2500.75' and hotel.json()['currency']=='USD'
    hotel_id=hotel.json()['id']
    edited_hotel=client.put(f'/api/v1/hotels/{hotel_id}',json={'name':'Hotel Updated','visit_date':'2025-02-04','location':'Toledo','total_price':'3000.50','currency':'UYU','ratings':[{'user_id':1,'score':7,'opinion':'Ok'},{'user_id':2,'score':9,'opinion':'Muy bien'}]},headers=h)
    assert client.delete(f'/api/v1/hotels/{hotel_id}',headers=h).status_code==204
    assert client.get('/api/v1/media',headers={}).status_code==401
    assert client.get('/api/v1/hotels',headers={}).status_code==401
def test_admin_user_management_and_password_flow():
    with SessionLocal() as db:
        db.query(User).filter(User.email=='a@example.com').update({'is_admin':True})
        db.commit()
    admin_token=client.post('/api/v1/auth/login',data={'username':'a@example.com','password':'password123'}).json()['access_token']
    ah={'Authorization':f'Bearer {admin_token}'}
    created=client.post('/api/v1/users',json={'name':'Temp User','email':'temp@example.com','password':'temporary123'},headers=ah)
    assert created.status_code==201 and created.json()['must_change_password'] is True
    assert '$2b$' not in created.text
    with SessionLocal() as db:
        stored=db.query(User).filter(User.email=='temp@example.com').one()
        assert stored.hashed_password != 'temporary123' and stored.hashed_password.startswith('$2b$')
    assert client.post('/api/v1/users',json={'name':'Duplicate','email':'temp@example.com','password':'temporary123'},headers=ah).status_code==409
    temp_login=client.post('/api/v1/auth/login',data={'username':'temp@example.com','password':'temporary123'})
    assert temp_login.status_code==200 and temp_login.json()['must_change_password'] is True
    temp_token=temp_login.json()['access_token']; th={'Authorization':f'Bearer {temp_token}'}
    assert client.post('/api/v1/auth/change-password',json={'new_password':'personal123','confirm_password':'personal123'},headers=th).status_code==200
    assert client.post('/api/v1/auth/login',data={'username':'temp@example.com','password':'temporary123'}).status_code==401
    assert client.post('/api/v1/auth/login',data={'username':'temp@example.com','password':'personal123'}).status_code==200
    assert client.post('/api/v1/auth/change-password',json={'current_password':'wrong123','new_password':'newpersonal123','confirm_password':'newpersonal123'},headers=th).status_code==400
    assert client.post('/api/v1/users',json={'name':'Nope','email':'nope@example.com','password':'temporary123'},headers=th).status_code==403
