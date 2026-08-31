from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel): name: str = Field(min_length=1,max_length=120); email: EmailStr; password: str = Field(min_length=8)
class UserOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; name:str; email:EmailStr; is_active:bool; created_at:datetime|None=None
class UserSummary(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; name:str
class Token(BaseModel): access_token:str; token_type:str='bearer'
class PlaceBase(BaseModel): name:str; visit_date:date; location:str|None=None; notes:str|None=None
class PlaceCreate(PlaceBase): pass
class RatingCreate(BaseModel): score:float=Field(ge=1,le=10); comment:str|None=None
class RatingOut(RatingCreate): model_config=ConfigDict(from_attributes=True); id:int; user_id:int; visit_id:int; created_at:datetime|None=None; user:UserSummary
class DishCreate(BaseModel): name:str; description:str|None=None; visit_id:int; user_id:int|None=None; score:float=Field(ge=1,le=10); notes:str|None=None
class DishOut(DishCreate): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; user:UserSummary|None=None
class PlaceOut(PlaceBase): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; average_rating:float|None=None
class SharedDish(BaseModel): name:str; description:str|None=None; score:float=Field(ge=1,le=10); notes:str|None=None
class PlaceEntry(BaseModel): user_id:int; dish:SharedDish; rating:RatingCreate
class PlaceComplete(BaseModel): place:PlaceBase; entries:list[PlaceEntry]=Field(min_length=2,max_length=2)
class PlaceDetail(PlaceOut): ratings:list[RatingOut]=[]; dishes:list[DishOut]=[]

class TestCreate(BaseModel): title:str; result:str; test_date:date; notes:str|None=None
class TestOutcomeCreate(BaseModel): user_id:int; result:str
class TestOutcomeOut(TestOutcomeCreate): model_config=ConfigDict(from_attributes=True); id:int; test_record_id:int; image_path:str|None=None; user:UserSummary
class TestOut(TestCreate): model_config=ConfigDict(from_attributes=True); id:int; image_path:str|None=None; created_at:datetime|None=None; updated_at:datetime|None=None; outcomes:list[TestOutcomeOut]=[]
class TestComplete(BaseModel): title:str; test_date:date; notes:str|None=None; outcomes:list[TestOutcomeCreate]=Field(min_length=2,max_length=2)
