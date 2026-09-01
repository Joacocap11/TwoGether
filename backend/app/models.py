from datetime import date, datetime
from enum import Enum
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Float, Boolean, func, UniqueConstraint, Enum as SQLEnum
class PlaceCategory(str, Enum):
    LUNCH='lunch'
    SNACK='snack'
    DINNER='dinner'
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    ratings=relationship('UserRating', back_populates='user')
    dishes=relationship('Dish', back_populates='user')
    test_outcomes=relationship('TestOutcome', back_populates='user')

class PlaceVisit(Base):
    __tablename__='place_visits'
    category: Mapped[PlaceCategory|None]=mapped_column(SQLEnum(PlaceCategory,native_enum=False,length=6), nullable=True)
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200), index=True)
    visit_date: Mapped[date]=mapped_column(Date)
    location: Mapped[str|None]=mapped_column(String(300), nullable=True)
    notes: Mapped[str|None]=mapped_column(Text, nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime|None]=mapped_column(DateTime, nullable=True)
    ratings=relationship('UserRating', back_populates='visit', cascade='all, delete-orphan')
    dishes=relationship('Dish', back_populates='visit', cascade='all, delete-orphan')

class UserRating(Base):
    __tablename__='user_ratings'
    id: Mapped[int]=mapped_column(primary_key=True)
    score: Mapped[float]=mapped_column(Float)
    comment: Mapped[str|None]=mapped_column(Text, nullable=True)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'))
    visit_id: Mapped[int]=mapped_column(ForeignKey('place_visits.id'))
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    user=relationship('User', back_populates='ratings'); visit=relationship('PlaceVisit', back_populates='ratings')

class Dish(Base):
    __tablename__='dishes'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200))
    description: Mapped[str|None]=mapped_column(Text, nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    visit_id: Mapped[int]=mapped_column(ForeignKey('place_visits.id'))
    user_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'), nullable=True)
    score: Mapped[float]=mapped_column(Float)
    notes: Mapped[str|None]=mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    visit=relationship('PlaceVisit', back_populates='dishes'); user=relationship('User', back_populates='dishes')

class TestRecord(Base):
    __tablename__='test_records'
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(200))
    result: Mapped[str|None]=mapped_column(Text, nullable=True)
    test_date: Mapped[date]=mapped_column(Date)
    notes: Mapped[str|None]=mapped_column(Text, nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    outcomes=relationship('TestOutcome', back_populates='test_record', cascade='all, delete-orphan')


class TestOutcome(Base):
    __tablename__='test_outcomes'
    __table_args__=(UniqueConstraint('test_record_id','user_id',name='uq_test_outcome_record_user'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    test_record_id: Mapped[int]=mapped_column(ForeignKey('test_records.id'), nullable=False)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), nullable=False)
    result: Mapped[str|None]=mapped_column(Text, nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    test_record=relationship('TestRecord', back_populates='outcomes')
    user=relationship('User', back_populates='test_outcomes')
