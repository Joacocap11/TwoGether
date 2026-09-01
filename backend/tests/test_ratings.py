import os
os.environ['DATABASE_URL']='sqlite:///./test_twogether.db'
os.environ['TESTING']='true'
os.environ['REGISTRATION_ENABLED']='true'
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base,engine
Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
client=TestClient(app)
def token(email):
    client.post('/api/v1/auth/register',json={'name':email,'email':email,'password':'password123'})
    return client.post('/api/v1/auth/login',data={'username':email,'password':'password123'}).json()['access_token']
def test_rating_rules_and_average():
    joaco=token('a@example.com'); h={'Authorization':f'Bearer {joaco}'}
    p=client.post('/api/v1/places',json={'name':'Cafe','visit_date':'2025-01-01','location':'Madrid','category':'lunch'},headers=h).json()
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':0},headers=h).status_code==422
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':11},headers=h).status_code==422
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':5},headers=h).status_code==201
    selena=token('b@example.com'); h2={'Authorization':f'Bearer {selena}'}
    assert client.post(f"/api/v1/places/{p['id']}/ratings",json={'score':8},headers=h2).status_code==201
    assert client.post('/api/v1/dishes',json={'name':'Soup','visit_id':p['id'],'user_id':1,'score':4},headers=h).status_code==201
    assert client.post('/api/v1/dishes',json={'name':'Pasta','visit_id':p['id'],'user_id':2,'score':8},headers=h2).status_code==201
    detail=client.get(f"/api/v1/places/{p['id']}",headers=h).json()
    assert detail['place_average_rating']==6.5
    assert detail['dish_average_rating']==6
    assert len(detail['ratings'])==2 and len(detail['dishes'])==2
    assert len(detail['photos'])==0
    test=client.post('/api/v1/tests/complete',json={'title':'Check','test_date':'2025-01-02','outcomes':[{'user_id':1},{'user_id':2}]},headers=h)
    assert test.status_code==201
    assert test.json()['result'] is None
    complete=client.post('/api/v1/places/complete',json={'place':{'name':'Dinner','visit_date':'2025-01-03','category':'dinner'},'entries':[{'user_id':1,'dish':{'name':'A','score':6},'rating':{'score':7,'comment':'ok'}},{'user_id':2,'dish':{'name':'B','score':8},'rating':{'score':9,'comment':'great'}}]},headers=h).json()
    place_id=complete['id']
    assert client.put(f'/api/v1/places/{place_id}/complete',json={'place':{'name':'Dinner edited','visit_date':'2025-01-04','location':'Madrid','category':'snack'},'entries':[{'user_id':1,'dish':{'name':'A2','score':7},'rating':{'score':8,'comment':'updated'}},{'user_id':2,'dish':{'name':'B2','score':9},'rating':{'score':10,'comment':'updated'}}]},headers=h).status_code==200
    updated=client.get(f'/api/v1/places/{place_id}',headers=h).json()
    assert updated['id']==place_id and updated['name']=='Dinner edited'
    assert {d['name'] for d in updated['dishes']}=={'A2','B2'}
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
    media=client.post('/api/v1/media',json={'title':'The Film','media_type':'movie','watched_date':'2025-02-01','category':'Terror','ratings':[{'user_id':1,'score':8},{'user_id':2,'score':9}]},headers=h)
    assert media.status_code==201 and media.json()['average_rating']==8.5
    media_id=media.json()['id']
    edited=client.put(f'/api/v1/media/{media_id}',json={'title':'The Series','media_type':'series','watched_date':'2025-02-02','category':None,'ratings':[{'user_id':1,'score':7},{'user_id':2,'score':8}]},headers=h)
    assert edited.status_code==200 and edited.json()['id']==media_id and edited.json()['media_type']=='series'
    assert client.delete(f'/api/v1/media/{media_id}',headers=h).status_code==204
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Central','visit_date':'2025-02-03','location':'Madrid','ratings':[{'user_id':1,'score':6,'opinion':'Bien'},{'user_id':2,'score':10,'opinion':'Excelente'}]},headers=h)
    assert hotel.status_code==201 and hotel.json()['average_rating']==8
    hotel_id=hotel.json()['id']
    edited_hotel=client.put(f'/api/v1/hotels/{hotel_id}',json={'name':'Hotel Updated','visit_date':'2025-02-04','location':'Toledo','ratings':[{'user_id':1,'score':7,'opinion':'Ok'},{'user_id':2,'score':9,'opinion':'Muy bien'}]},headers=h)
    assert edited_hotel.status_code==200 and edited_hotel.json()['id']==hotel_id
    assert client.delete(f'/api/v1/hotels/{hotel_id}',headers=h).status_code==204
    assert client.get('/api/v1/media',headers={}).status_code==401
    assert client.get('/api/v1/hotels',headers={}).status_code==401
