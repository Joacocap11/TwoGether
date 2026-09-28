from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Float, Integer, Boolean, Numeric, func, UniqueConstraint, Enum as SQLEnum
class PlaceCategory(str, Enum):
    LUNCH='lunch'
    SNACK='snack'
    DINNER='dinner'
class SpotStatus(str, Enum):
    WISHLIST='wishlist'
    VISITED='visited'
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    is_admin: Mapped[bool]=mapped_column(Boolean, default=False)
    must_change_password: Mapped[bool]=mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    ratings=relationship('UserRating', back_populates='user')
    dishes=relationship('Dish', back_populates='user')
    test_outcomes=relationship('TestOutcome', back_populates='user')
    media_ratings=relationship('MediaRating', back_populates='user')
    hotel_ratings=relationship('HotelRating', back_populates='user')
    refresh_tokens=relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
    spot_ratings=relationship('SpotRating', back_populates='user')

class PlaceVisit(Base):
    __tablename__='place_visits'
    category: Mapped[PlaceCategory|None]=mapped_column(SQLEnum(PlaceCategory,native_enum=False,length=6), nullable=True)
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200), index=True)
    visit_date: Mapped[date]=mapped_column(Date)
    location: Mapped[str|None]=mapped_column(String(300), nullable=True)
    currency: Mapped[str|None]=mapped_column(String(3), nullable=True)
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
    dish_price: Mapped[Decimal|None]=mapped_column(Numeric(12,2), nullable=True)
    drink_price: Mapped[Decimal|None]=mapped_column(Numeric(12,2), nullable=True)
    dessert_price: Mapped[Decimal|None]=mapped_column(Numeric(12,2), nullable=True)
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

class MediaEntry(Base):
    __tablename__='media_entries'
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(200))
    media_type: Mapped[str]=mapped_column(String(6))
    watched_date: Mapped[date]=mapped_column(Date)
    category: Mapped[str|None]=mapped_column(String(120), nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    ratings=relationship('MediaRating', back_populates='media', cascade='all, delete-orphan')

class MediaRating(Base):
    __tablename__='media_ratings'
    __table_args__=(UniqueConstraint('media_entry_id','user_id',name='uq_media_rating_entry_user'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    media_entry_id: Mapped[int]=mapped_column(ForeignKey('media_entries.id'), nullable=False)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), nullable=False)
    score: Mapped[float]=mapped_column(Float)
    opinion: Mapped[str|None]=mapped_column(Text, nullable=True)
    media=relationship('MediaEntry', back_populates='ratings'); user=relationship('User', back_populates='media_ratings')
class HotelVisit(Base):
    __tablename__='hotel_visits'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200))
    visit_date: Mapped[date]=mapped_column(Date)
    location: Mapped[str|None]=mapped_column(String(300), nullable=True)
    total_price: Mapped[Decimal|None]=mapped_column(Numeric(12,2), nullable=True)
    currency: Mapped[str|None]=mapped_column(String(3), nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    ratings=relationship('HotelRating', back_populates='hotel', cascade='all, delete-orphan')

class HotelRating(Base):
    __tablename__='hotel_ratings'
    __table_args__=(UniqueConstraint('hotel_visit_id','user_id',name='uq_hotel_rating_visit_user'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    hotel_visit_id: Mapped[int]=mapped_column(ForeignKey('hotel_visits.id'), nullable=False)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), nullable=False)
    score: Mapped[float]=mapped_column(Float)
    opinion: Mapped[str|None]=mapped_column(Text, nullable=True)
    hotel=relationship('HotelVisit', back_populates='ratings')
    user=relationship('User', back_populates='hotel_ratings')

class RefreshToken(Base):
    __tablename__='refresh_tokens'
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    token_hash: Mapped[str]=mapped_column(String(64), unique=True, index=True)
    family_id: Mapped[str]=mapped_column(String(32), index=True)
    expires_at: Mapped[datetime]=mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime|None]=mapped_column(DateTime, nullable=True)
    revoked_reason: Mapped[str|None]=mapped_column(String(20), nullable=True)
    replaced_by_id: Mapped[int|None]=mapped_column(ForeignKey('refresh_tokens.id'), nullable=True)
    user_agent: Mapped[str|None]=mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    user=relationship('User', back_populates='refresh_tokens', foreign_keys=[user_id])

class Spot(Base):
    __tablename__='spots'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200), index=True)
    location: Mapped[str|None]=mapped_column(String(300), nullable=True)
    visit_date: Mapped[date|None]=mapped_column(Date, nullable=True)
    notes: Mapped[str|None]=mapped_column(Text, nullable=True)
    image_path: Mapped[str|None]=mapped_column(String(500), nullable=True)
    status: Mapped[SpotStatus]=mapped_column(SQLEnum(SpotStatus,native_enum=False,length=8), nullable=False, server_default=SpotStatus.WISHLIST.name)
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    ratings=relationship('SpotRating', back_populates='spot', cascade='all, delete-orphan')

class SpotRating(Base):
    # Score is a real Integer (unlike UserRating/MediaRating/HotelRating, which
    # store score as Float): the product spec for Spots explicitly requires an
    # integer 1-10 scale, so this intentionally does not reuse the Float
    # convention of the other three rating models.
    __tablename__='spot_ratings'
    __table_args__=(UniqueConstraint('spot_id','user_id',name='uq_spot_rating_spot_user'),)
    id: Mapped[int]=mapped_column(primary_key=True)
    score: Mapped[int]=mapped_column(Integer, nullable=False)
    comment: Mapped[str|None]=mapped_column(Text, nullable=True)
    spot_id: Mapped[int]=mapped_column(ForeignKey('spots.id'))
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    spot=relationship('Spot', back_populates='ratings')
    user=relationship('User', back_populates='spot_ratings')
