from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel): name: str = Field(min_length=1,max_length=120); email: EmailStr; password: str = Field(min_length=8)
class UserOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; name:str; email:EmailStr; is_active:bool; created_at:datetime|None=None
class Token(BaseModel): access_token:str; token_type:str='bearer'
class PlaceBase(BaseModel): name:str; visit_date:date; location:str|None=None; notes:str|None=None
class PlaceCreate(PlaceBase): pass
class PlaceOut(PlaceBase): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; average_rating:float|None=None
class RatingCreate(BaseModel): score:float=Field(ge=1,le=10); comment:str|None=None
class RatingOut(RatingCreate): model_config=ConfigDict(from_attributes=True); id:int; user_id:int; visit_id:int; created_at:datetime|None=None
class DishCreate(BaseModel): name:str; description:str|None=None; visit_id:int; user_id:int|None=None; score:float=Field(ge=1,le=10); notes:str|None=None
class DishOut(DishCreate): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None
class TestCreate(BaseModel): title:str; result:str; test_date:date; notes:str|None=None
class TestOut(TestCreate): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None
