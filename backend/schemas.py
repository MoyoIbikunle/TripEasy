from pydantic import BaseModel, EmailStr, Field
from datetime import date
from datetime import time
from decimal import Decimal
from typing import Optional
from datetime import date as date_type

#this is the structure of what the FastAPI expects to get
#after the register button is clicked 
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    password: str = Field(min_length=8)

#this is the structure of what the frontend expects to get from the backend
# to be able to respond with e.g. new user..... 
class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class TripCreate(BaseModel):
    name: str
    start_date: date
    end_date: date

class TripOut(BaseModel):
    trip_id: int
    name: str
    start_date: date
    end_date: date
    invite_code: str

    class Config:
        from_attributes = True

class ActivityCreate(BaseModel):
    name: str
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    address: Optional[str] = None
    cost: Optional[Decimal] = None

class ActivityOut(BaseModel):
    activity_id: int
    trip_id: int
    name: str
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    address: Optional[str] = None
    cost: Optional[Decimal] = None

class ActivityResponseCreate(BaseModel):
    status: str

class ActivityResponseOut(BaseModel):
    response_id: int
    user_id: int
    activity_id: int
    status: str

    class Config:
        from_attributes = True

class AccommodationCreate(BaseModel):
    address: str
    check_in_date: Optional[date_type] = None
    check_out_date: Optional[date_type] = None

class AccommodationOut(BaseModel):
    accommodation_id: int
    trip_id: int
    address: str
    check_in_date: Optional[date_type] = None
    check_out_date: Optional[date_type] = None

    class Config:
        from_attributes = True

#this allows us to establish that connection 
#class Membership(Base):
 #...user = relationship("Users", back_populates="memberships")
class MembershipOut(BaseModel):
    membership_id: int
    role: str
    user: UserOut

    class Config:
        from_attributes = True