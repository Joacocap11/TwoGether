from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .models import PlaceCategory

class UserCreate(BaseModel): name: str = Field(min_length=1,max_length=120); email: EmailStr; password: str = Field(min_length=8)
class UserOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; name:str; email:EmailStr; is_active:bool; is_admin:bool; must_change_password:bool; created_at:datetime|None=None
class UserSummary(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; name:str
class AdminUserCreate(UserCreate): pass
class PasswordChange(BaseModel): current_password:str|None=None; new_password:str=Field(min_length=8); confirm_password:str=Field(min_length=8)
class Token(BaseModel): access_token:str; token_type:str='bearer'; must_change_password:bool=False
class PlaceBase(BaseModel): name:str; visit_date:date; location:str|None=None; notes:str|None=None; category:PlaceCategory|None=None
class PlaceCreate(PlaceBase): category:PlaceCategory
class RatingCreate(BaseModel): score:float=Field(ge=1,le=10); comment:str|None=None
class RatingOut(RatingCreate): model_config=ConfigDict(from_attributes=True); id:int; user_id:int; visit_id:int; created_at:datetime|None=None; user:UserSummary
class DishCreate(BaseModel): name:str; visit_id:int; user_id:int|None=None; score:float=Field(ge=1,le=10)
class DishOut(DishCreate): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; user:UserSummary|None=None
class PlaceOut(PlaceBase): model_config=ConfigDict(from_attributes=True); id:int; category:PlaceCategory|None=None; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; average_rating:float|None=None; place_average_rating:float|None=None; dish_average_rating:float|None=None; ratings:list[RatingOut]=[]; dishes:list[DishOut]=[]; photos:list[str]=[]
class SharedDish(BaseModel): name:str; score:float=Field(ge=1,le=10)
class PlaceEntry(BaseModel): user_id:int; dish:SharedDish; rating:RatingCreate
class PlaceComplete(BaseModel): place:PlaceCreate; entries:list[PlaceEntry]=Field(min_length=2,max_length=2)
class PlaceDetail(PlaceOut): pass

class TestCreate(BaseModel): title:str; test_date:date; notes:str|None=None
class TestOutcomeCreate(BaseModel): user_id:int
class TestOutcomeOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; test_record_id:int; user_id:int; result:str|None=None; image_path:str|None=None; user:UserSummary

class MediaRatingCreate(BaseModel): user_id:int; score:float=Field(ge=1,le=10); opinion:str|None=None
class MediaRatingOut(MediaRatingCreate): model_config=ConfigDict(from_attributes=True); id:int
class MediaCreate(BaseModel):
    title:str; media_type:str=Field(pattern='^(series|movie)$'); watched_date:date; category:str|None=None
    ratings:list[MediaRatingCreate]=Field(min_length=2,max_length=2)
class MediaOut(MediaCreate):
    model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; ratings:list[MediaRatingOut]=[]; average_rating:float|None=None
class HotelRatingCreate(BaseModel): user_id:int; score:float=Field(ge=1,le=10); opinion:str|None=None
class HotelRatingOut(HotelRatingCreate): model_config=ConfigDict(from_attributes=True); id:int
class HotelCreate(BaseModel):
    name:str; visit_date:date; location:str|None=None; ratings:list[HotelRatingCreate]=Field(min_length=2,max_length=2)
class HotelOut(HotelCreate):
    model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; ratings:list[HotelRatingOut]=[]; average_rating:float|None=None
class TestOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; title:str; result:str|None=None; test_date:date; notes:str|None=None; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; outcomes:list[TestOutcomeOut]=[]
class TestComplete(BaseModel): title:str; test_date:date; notes:str|None=None; outcomes:list[TestOutcomeCreate]=Field(min_length=2,max_length=2)
