import os
os.environ['DATABASE_URL']='sqlite:///./test_twogether.db'
os.environ['TESTING']='true'
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
    p=client.post('/api/v1/places',json={'name':'Cafe','visit_date':'2025-01-01','location':'Madrid'},headers=h).json()
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
    assert all(outcome['result'] is None for outcome in test.json()['outcomes'])
