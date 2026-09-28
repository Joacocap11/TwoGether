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

def _hotel_ratings():
    return [{'user_id':1,'score':7,'opinion':None},{'user_id':2,'score':8,'opinion':None}]

def test_hotel_amenity_a_joaco_rates_pool():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Piscina A','visit_date':'2025-03-01','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    r=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':9},headers=hj)
    assert r.status_code==200 and r.json()['user_id']==joaco_id and r.json()['score']==9

def test_hotel_amenity_b_selena_rates_pool():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    selena_id=uid('b@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Piscina B','visit_date':'2025-03-02','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    r=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{selena_id}",json={'score':7},headers=hj)
    assert r.status_code==200 and r.json()['user_id']==selena_id and r.json()['score']==7

def test_hotel_amenity_c_pool_average_correct():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com'); selena_id=uid('b@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Piscina C','visit_date':'2025-03-03','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':9},headers=hj)
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{selena_id}",json={'score':7},headers=hj)
    detail=client.get(f"/api/v1/hotels/{hotel['id']}",headers=hj).json()
    assert detail['pool_average_rating']==8.0
    assert {r['score'] for r in detail['pool_ratings']}=={9,7}

def test_hotel_amenity_d_joaco_rates_breakfast():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Desayuno D','visit_date':'2025-03-04','has_breakfast':True,'ratings':_hotel_ratings()},headers=hj).json()
    r=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/breakfast/{joaco_id}",json={'score':8},headers=hj)
    assert r.status_code==200 and r.json()['score']==8

def test_hotel_amenity_e_selena_rates_breakfast():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    selena_id=uid('b@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Desayuno E','visit_date':'2025-03-05','has_breakfast':True,'ratings':_hotel_ratings()},headers=hj).json()
    r=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/breakfast/{selena_id}",json={'score':9},headers=hj)
    assert r.status_code==200 and r.json()['score']==9

def test_hotel_amenity_f_breakfast_average_correct():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com'); selena_id=uid('b@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Desayuno F','visit_date':'2025-03-06','has_breakfast':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/breakfast/{joaco_id}",json={'score':8},headers=hj)
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/breakfast/{selena_id}",json={'score':9},headers=hj)
    detail=client.get(f"/api/v1/hotels/{hotel['id']}",headers=hj).json()
    assert detail['breakfast_average_rating']==8.5

def test_hotel_amenity_g_single_rating_average_equals_that_score():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Solo Rating','visit_date':'2025-03-07','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':6},headers=hj)
    detail=client.get(f"/api/v1/hotels/{hotel['id']}",headers=hj).json()
    assert detail['pool_average_rating']==6 and len(detail['pool_ratings'])==1

def test_hotel_amenity_h_joaco_session_edits_selena_rating():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    selena_id=uid('b@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Cross H','visit_date':'2025-03-08','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    r=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{selena_id}",json={'score':10},headers=hj)
    assert r.status_code==200 and r.json()['user_id']==selena_id

def test_hotel_amenity_i_selena_session_edits_joaco_rating():
    hs={'Authorization':f'Bearer {token("b@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Cross I','visit_date':'2025-03-09','has_pool':True,'ratings':_hotel_ratings()},headers=hs).json()
    r=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':5},headers=hs)
    assert r.status_code==200 and r.json()['user_id']==joaco_id

def test_hotel_amenity_j_unique_hotel_user_amenity_upserts_no_duplicate():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Unique J','visit_date':'2025-03-10','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':4},headers=hj)
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':5},headers=hj)
    updated=client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':6},headers=hj)
    assert updated.status_code==200
    detail=client.get(f"/api/v1/hotels/{hotel['id']}",headers=hj).json()
    joaco_rows=[r for r in detail['pool_ratings'] if r['user_id']==joaco_id]
    assert len(joaco_rows)==1 and joaco_rows[0]['score']==6

def test_hotel_amenity_k_score_below_range_rejected():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Invalido K','visit_date':'2025-03-11','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    assert client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':0},headers=hj).status_code==422

def test_hotel_amenity_l_score_above_range_rejected():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Invalido L','visit_date':'2025-03-12','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    assert client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':11},headers=hj).status_code==422

def test_hotel_amenity_m_nonexistent_user_rejected():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Invalido M','visit_date':'2025-03-13','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    assert client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/999999",json={'score':5},headers=hj).status_code==404

def test_hotel_amenity_n_pool_rating_rejected_if_no_pool():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Sin Piscina N','visit_date':'2025-03-14','ratings':_hotel_ratings()},headers=hj).json()
    assert client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':7},headers=hj).status_code==409

def test_hotel_amenity_o_breakfast_rating_rejected_if_no_breakfast():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Sin Desayuno O','visit_date':'2025-03-15','ratings':_hotel_ratings()},headers=hj).json()
    assert client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/breakfast/{joaco_id}",json={'score':7},headers=hj).status_code==409

def test_hotel_amenity_p_disable_pool_keeps_ratings_hidden():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Toggle P','visit_date':'2025-03-16','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':9},headers=hj)
    updated=client.put(f"/api/v1/hotels/{hotel['id']}",json={'name':'Hotel Toggle P','visit_date':'2025-03-16','has_pool':False,'ratings':_hotel_ratings()},headers=hj).json()
    assert updated['pool_ratings']==[] and updated['pool_average_rating'] is None

def test_hotel_amenity_q_reenable_pool_restores_ratings():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Toggle Q','visit_date':'2025-03-17','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/pool/{joaco_id}",json={'score':9},headers=hj)
    client.put(f"/api/v1/hotels/{hotel['id']}",json={'name':'Hotel Toggle Q','visit_date':'2025-03-17','has_pool':False,'ratings':_hotel_ratings()},headers=hj)
    restored=client.put(f"/api/v1/hotels/{hotel['id']}",json={'name':'Hotel Toggle Q','visit_date':'2025-03-17','has_pool':True,'ratings':_hotel_ratings()},headers=hj).json()
    assert restored['pool_average_rating']==9 and len(restored['pool_ratings'])==1

def test_hotel_amenity_r_breakfast_disable_enable_cycle():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    hotel=client.post('/api/v1/hotels',json={'name':'Hotel Toggle R','visit_date':'2025-03-18','has_breakfast':True,'ratings':_hotel_ratings()},headers=hj).json()
    client.put(f"/api/v1/hotels/{hotel['id']}/amenity-ratings/breakfast/{joaco_id}",json={'score':7},headers=hj)
    off=client.put(f"/api/v1/hotels/{hotel['id']}",json={'name':'Hotel Toggle R','visit_date':'2025-03-18','has_breakfast':False,'ratings':_hotel_ratings()},headers=hj).json()
    assert off['breakfast_ratings']==[] and off['breakfast_average_rating'] is None
    on=client.put(f"/api/v1/hotels/{hotel['id']}",json={'name':'Hotel Toggle R','visit_date':'2025-03-18','has_breakfast':True,'ratings':_hotel_ratings()},headers=hj).json()
    assert on['breakfast_average_rating']==7 and len(on['breakfast_ratings'])==1

def test_hotel_amenity_s_historical_hotel_without_amenities_still_works():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    r=client.post('/api/v1/hotels',json={'name':'Hotel Historico S','visit_date':'2025-03-19','location':'Colonia','total_price':'1200.00','currency':'UYU','ratings':_hotel_ratings()},headers=hj)
    assert r.status_code==201
    d=r.json()
    assert d['has_pool'] is False and d['has_breakfast'] is False
    assert d['pool_ratings']==[] and d['pool_average_rating'] is None
    assert d['breakfast_ratings']==[] and d['breakfast_average_rating'] is None
    assert d['total_price']=='1200.00' and d['currency']=='UYU'


def test_spot_a_create_wishlist_minimal():
    joaco=token('a@example.com'); hj={'Authorization':f'Bearer {joaco}'}
    spot=client.post('/api/v1/spots',json={'name':'Parque Rodo'},headers=hj).json()
    assert spot['status']=='wishlist' and spot['visit_date'] is None and spot['ratings']==[] and spot['average_rating'] is None

def test_spot_b_create_visited_with_visit_date():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Cabo Polonio','status':'visited','visit_date':'2025-06-01'},headers=hj).json()
    assert spot['status']=='visited' and spot['visit_date']=='2025-06-01'

def test_spot_c_d_e_f_list_all_and_status_filter():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    client.post('/api/v1/spots',json={'name':'Wishlist Only'},headers=hj)
    client.post('/api/v1/spots',json={'name':'Visited Only','status':'visited'},headers=hj)
    everyone=client.get('/api/v1/spots',headers=hj).json()
    assert {s['name'] for s in everyone}>={'Wishlist Only','Visited Only'}
    wishlist_only=client.get('/api/v1/spots?status=wishlist',headers=hj).json()
    assert all(s['status']=='wishlist' for s in wishlist_only)
    assert 'Wishlist Only' in {s['name'] for s in wishlist_only}
    assert 'Visited Only' not in {s['name'] for s in wishlist_only}
    visited_only=client.get('/api/v1/spots?status=visited',headers=hj).json()
    assert all(s['status']=='visited' for s in visited_only)
    assert 'Visited Only' in {s['name'] for s in visited_only}
    assert 'Wishlist Only' not in {s['name'] for s in visited_only}
    assert client.get('/api/v1/spots?status=bogus',headers=hj).status_code==422

def test_spot_g_h_wishlist_visited_transitions_clear_visit_date():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Punta del Diablo'},headers=hj).json()
    assert spot['visit_date'] is None
    visited=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'Punta del Diablo','status':'visited','visit_date':'2025-07-04'},headers=hj)
    assert visited.status_code==200 and visited.json()['status']=='visited' and visited.json()['visit_date']=='2025-07-04'
    back=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'Punta del Diablo','status':'wishlist','visit_date':'2025-07-04'},headers=hj)
    assert back.status_code==200 and back.json()['status']=='wishlist' and back.json()['visit_date'] is None

def test_spot_i_ratings_survive_visited_wishlist_visited():
    joaco=token('a@example.com'); hj={'Authorization':f'Bearer {joaco}'}
    selena=token('b@example.com'); hs={'Authorization':f'Bearer {selena}'}
    spot=client.post('/api/v1/spots',json={'name':'Cerro Pan de Azucar','status':'visited'},headers=hj).json()
    client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':9,'comment':'Lindo'},headers=hj)
    client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':7,'comment':'Ok'},headers=hs)
    hidden=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'Cerro Pan de Azucar','status':'wishlist'},headers=hj)
    assert hidden.json()['ratings']==[] and hidden.json()['average_rating'] is None
    assert client.get(f"/api/v1/spots/{spot['id']}/ratings",headers=hj).json()==[]
    restored=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'Cerro Pan de Azucar','status':'visited'},headers=hj)
    assert len(restored.json()['ratings'])==2 and restored.json()['average_rating']==8
    assert {r['score'] for r in restored.json()['ratings']}=={9,7}

def test_spot_j_rating_rejected_while_wishlist():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Laguna Garzon'},headers=hj).json()
    assert client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':6},headers=hj).status_code==409
    assert client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':0},headers=hj).status_code==422
    assert client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':11},headers=hj).status_code==422

def test_spot_k_l_m_two_users_rate_separately_average_and_comments():
    joaco=token('a@example.com'); hj={'Authorization':f'Bearer {joaco}'}
    selena=token('b@example.com'); hs={'Authorization':f'Bearer {selena}'}
    spot=client.post('/api/v1/spots',json={'name':'Playa Grande','status':'visited'},headers=hj).json()
    rj=client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':9,'comment':'Me encanto el verde que tenia.'},headers=hj)
    assert rj.status_code==201 and rj.json()['comment']=='Me encanto el verde que tenia.'
    assert client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':7},headers=hj).status_code==409
    rs=client.post(f"/api/v1/spots/{spot['id']}/ratings",json={'score':8},headers=hs)
    assert rs.status_code==201 and rs.json()['comment'] is None
    detail=client.get(f"/api/v1/spots/{spot['id']}",headers=hj).json()
    assert len(detail['ratings'])==2 and detail['average_rating']==8.5
    updated=client.put(f"/api/v1/spots/{spot['id']}/ratings/me",json={'score':10,'comment':'Aun mejor la segunda vez'},headers=hj)
    assert updated.status_code==200 and updated.json()['score']==10
    fresh_spot=client.post('/api/v1/spots',json={'name':'Isla de Lobos','status':'visited'},headers=hj).json()
    assert client.put(f"/api/v1/spots/{fresh_spot['id']}/ratings/me",json={'score':5},headers=hs).status_code==404
    unaffected=client.get(f"/api/v1/spots/{spot['id']}",headers=hj).json()
    selena_row=[r for r in unaffected['ratings'] if r['user_id']==rs.json()['user_id']][0]
    assert selena_row['score']==8 and unaffected['average_rating']==9

def test_spot_n_upload_image():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Punta Ballena'},headers=hj).json()
    uploaded=client.post(f"/api/v1/spots/{spot['id']}/upload",files={'image':('spot.png',b'spot','image/png')},headers=hj)
    assert uploaded.status_code==200 and uploaded.json()['image_path']

def test_spot_o_delete():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Aguas Dulces'},headers=hj).json()
    assert client.delete(f"/api/v1/spots/{spot['id']}",headers=hj).status_code==204
    assert client.get(f"/api/v1/spots/{spot['id']}",headers=hj).status_code==404

def test_spot_p_create_with_description():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Parque Rodo','description':'Parque amplio con lago y zonas verdes.','notes':'Ir un domingo de tarde.'},headers=hj).json()
    assert spot['description']=='Parque amplio con lago y zonas verdes.' and spot['notes']=='Ir un domingo de tarde.'

def test_spot_q_create_without_description():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Sin Descripcion'},headers=hj).json()
    assert spot['description'] is None

def test_spot_r_create_with_valid_category():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Cerro Catedral','category':'viewpoint'},headers=hj).json()
    assert spot['category']=='viewpoint'

def test_spot_s_create_with_null_category():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Sin Categoria'},headers=hj).json()
    assert spot['category'] is None

def test_spot_t_create_with_invalid_category_rejected():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    assert client.post('/api/v1/spots',json={'name':'Categoria Invalida','category':'bogus'},headers=hj).status_code==422

def test_spot_u_update_category():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Museo Historico','category':'museum'},headers=hj).json()
    updated=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'Museo Historico','category':'cultural','status':'wishlist'},headers=hj)
    assert updated.status_code==200 and updated.json()['category']=='cultural'

def test_spot_v_category_filter():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    client.post('/api/v1/spots',json={'name':'Playa Filtrable','category':'beach'},headers=hj)
    client.post('/api/v1/spots',json={'name':'Parque Filtrable','category':'park'},headers=hj)
    beaches=client.get('/api/v1/spots?category=beach',headers=hj).json()
    assert all(s['category']=='beach' for s in beaches)
    assert 'Playa Filtrable' in {s['name'] for s in beaches}
    assert 'Parque Filtrable' not in {s['name'] for s in beaches}
    assert client.get('/api/v1/spots?category=bogus',headers=hj).status_code==422

def test_spot_w_status_and_category_filters_combined():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    client.post('/api/v1/spots',json={'name':'Parque Visitado','category':'park','status':'visited'},headers=hj)
    client.post('/api/v1/spots',json={'name':'Parque Deseado','category':'park'},headers=hj)
    result=client.get('/api/v1/spots?status=visited&category=park',headers=hj).json()
    assert all(s['status']=='visited' and s['category']=='park' for s in result)
    assert 'Parque Visitado' in {s['name'] for s in result}
    assert 'Parque Deseado' not in {s['name'] for s in result}

def uid(email):
    with SessionLocal() as db:
        return db.query(User).filter_by(email=email).first().id

def test_spot_x_a_joaco_session_edits_joaco_rating():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    token('b@example.com')
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Rambla Sur','status':'visited'},headers=hj).json()
    r=client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9,'comment':'Lindo atardecer'},headers=hj)
    assert r.status_code==200 and r.json()['user_id']==joaco_id and r.json()['score']==9

def test_spot_x_b_joaco_session_edits_selena_rating():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    selena_id=uid('b@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Termas del Dayman','status':'visited'},headers=hj).json()
    r=client.put(f"/api/v1/spots/{spot['id']}/ratings/{selena_id}",json={'score':7,'comment':'Agua calentita'},headers=hj)
    assert r.status_code==200 and r.json()['user_id']==selena_id and r.json()['score']==7

def test_spot_x_c_selena_session_edits_joaco_rating():
    hs={'Authorization':f'Bearer {token("b@example.com")}'}
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Valizas','status':'visited'},headers=hs).json()
    r=client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':8},headers=hs)
    assert r.status_code==200 and r.json()['user_id']==joaco_id and r.json()['score']==8

def test_spot_x_d_selena_session_edits_selena_rating():
    hs={'Authorization':f'Bearer {token("b@example.com")}'}
    selena_id=uid('b@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Jose Ignacio','status':'visited'},headers=hs).json()
    r=client.put(f"/api/v1/spots/{spot['id']}/ratings/{selena_id}",json={'score':10},headers=hs)
    assert r.status_code==200 and r.json()['user_id']==selena_id and r.json()['score']==10

def test_spot_x_e_upsert_never_duplicates_unique_constraint():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Piriapolis','status':'visited'},headers=hj).json()
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':5},headers=hj)
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':6},headers=hj)
    updated=client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9,'comment':'final'},headers=hj)
    assert updated.status_code==200
    detail=client.get(f"/api/v1/spots/{spot['id']}",headers=hj).json()
    joaco_rows=[r for r in detail['ratings'] if r['user_id']==joaco_id]
    assert len(joaco_rows)==1 and joaco_rows[0]['score']==9 and joaco_rows[0]['comment']=='final'

def test_spot_x_f_nonexistent_user_id_rejected():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Colonia Sacramento','status':'visited'},headers=hj).json()
    assert client.put(f"/api/v1/spots/{spot['id']}/ratings/999999",json={'score':5},headers=hj).status_code==404

def test_spot_x_g_create_visited_directly():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    spot=client.post('/api/v1/spots',json={'name':'Cabo Santa Maria','status':'visited','visit_date':'2026-02-10'},headers=hj).json()
    assert spot['status']=='visited' and spot['visit_date']=='2026-02-10' and spot['ratings']==[]

def test_spot_x_h_visited_direct_with_rating_only_joaco():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Sierra de las Animas','status':'visited'},headers=hj).json()
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9},headers=hj)
    detail=client.get(f"/api/v1/spots/{spot['id']}",headers=hj).json()
    assert len(detail['ratings'])==1 and detail['average_rating']==9

def test_spot_x_i_visited_direct_with_both_ratings():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com'); selena_id=uid('b@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Laguna Garzon','status':'visited'},headers=hj).json()
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9},headers=hj)
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{selena_id}",json={'score':7},headers=hj)
    detail=client.get(f"/api/v1/spots/{spot['id']}",headers=hj).json()
    assert len(detail['ratings'])==2

def test_spot_x_j_average_correct():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com'); selena_id=uid('b@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Punta Espinillo','status':'visited'},headers=hj).json()
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9},headers=hj)
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{selena_id}",json={'score':8},headers=hj)
    detail=client.get(f"/api/v1/spots/{spot['id']}",headers=hj).json()
    assert detail['average_rating']==8.5

def test_spot_x_k_wishlist_hides_and_rejects_ratings():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Chihuahua'},headers=hj).json()
    assert spot['ratings']==[]
    assert client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':5},headers=hj).status_code==409

def test_spot_x_l_visited_to_wishlist_keeps_ratings():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'Solis','status':'visited'},headers=hj).json()
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9},headers=hj)
    back=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'Solis','status':'wishlist'},headers=hj).json()
    assert back['ratings']==[] and back['average_rating'] is None

def test_spot_x_m_wishlist_to_visited_restores_ratings():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    joaco_id=uid('a@example.com')
    spot=client.post('/api/v1/spots',json={'name':'La Paloma','status':'visited'},headers=hj).json()
    client.put(f"/api/v1/spots/{spot['id']}/ratings/{joaco_id}",json={'score':9},headers=hj)
    client.put(f"/api/v1/spots/{spot['id']}",json={'name':'La Paloma','status':'wishlist'},headers=hj)
    restored=client.put(f"/api/v1/spots/{spot['id']}",json={'name':'La Paloma','status':'visited','visit_date':'2026-03-01'},headers=hj).json()
    assert len(restored['ratings'])==1 and restored['ratings'][0]['score']==9 and restored['average_rating']==9

def test_spot_x_n_category_filter_still_works_backend():
    hj={'Authorization':f'Bearer {token("a@example.com")}'}
    client.post('/api/v1/spots',json={'name':'Museo Filtro Backend','category':'museum'},headers=hj)
    result=client.get('/api/v1/spots?category=museum',headers=hj).json()
    assert all(s['category']=='museum' for s in result)
    assert 'Museo Filtro Backend' in {s['name'] for s in result}



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
