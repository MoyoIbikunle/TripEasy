from sqlalchemy import Column, Integer, String, Date, Time, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Trip(Base):
    __tablename__ = "trip"
    trip_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    invite_code = Column(String(50), unique=True)

    memberships = relationship("Membership", back_populates="trip")
    accommodations = relationship("Accommodation", back_populates="trip")
    activities = relationship("Activity", back_populates="trip")


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20))
    password_hash = Column(String(255), nullable=False)

    memberships = relationship("Membership", back_populates="user")
    responses = relationship("ActivityResponse", back_populates="user")


class Membership(Base):
    __tablename__ = "membership"
    membership_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    trip_id = Column(Integer, ForeignKey("trip.trip_id"))
    role = Column(String(50), nullable=False)

    user = relationship("Users", back_populates="memberships")
    trip = relationship("Trip", back_populates="memberships")


class Accommodation(Base):
    __tablename__ = "accommodation"
    accommodation_id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey("trip.trip_id"))
    address = Column(String(255))
    check_in_date = Column(Date)
    check_out_date = Column(Date)

    trip = relationship("Trip", back_populates="accommodations")


class Activity(Base):
    __tablename__ = "activity"
    activity_id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey("trip.trip_id"))
    name = Column(String(255), nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    address = Column(String(255))
    cost = Column(Numeric(10, 2))

    trip = relationship("Trip", back_populates="activities")
    responses = relationship("ActivityResponse", back_populates="activity")


class ActivityResponse(Base):
    __tablename__ = "activity_response"
    response_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    activity_id = Column(Integer, ForeignKey("activity.activity_id"))
    status = Column(String(20), nullable=False)

    user = relationship("Users", back_populates="responses")
    activity = relationship("Activity", back_populates="responses")