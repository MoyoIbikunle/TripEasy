from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Users
from schemas import UserCreate, UserOut, UserLogin, TripCreate, TripOut, ActivityCreate, ActivityOut, AccommodationCreate, AccommodationOut, ActivityResponseCreate, ActivityResponseOut, MembershipOut
from auth import hash_password, verify_password, create_access_token, get_current_user
from models import Users, Trip, Membership, Activity, Accommodation, ActivityResponse
from dotenv import load_dotenv
from google import genai
from fastapi.middleware.cors import CORSMiddleware
import secrets
import os

app = FastAPI()
#permits frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#reads .env file containing apikey
load_dotenv()
#looks up the specifc value saved under GEMINI_API_KEY
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

#register method decorator, when register url is visited respond using userout structure
@app.post("/register", response_model=UserOut)
#Depends: before running the function, call get_db(), whatever it yields pass that into db
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    #checking users table for an email that matches our user_data email
    existing_user = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = Users(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password_hash=hash_password(user_data.password)
    )

    #prepares for saving 
    db.add(new_user)
    #saves it
    db.commit()
    #reloads new_user form dtatbase, so it gets an id 
    db.refresh(new_user)

    #response model takes this 
    return new_user


#login method decorator, when login url is visited run this function
@app.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    #find the user in the database matching this email
    user = db.query(Users).filter(Users.email == login_data.email).first()

    #if no user found OR password doesn't match the stored hash, reject with the same generic error either way
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    #generate a JWT token embedding this user's email, using official JWT standards like sub
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserOut)
def read_current_user(current_user: Users = Depends(get_current_user)):
    return current_user

#invite code generator using pythons library secrets 
def generate_invite_code():
    return secrets.token_urlsafe(8)

@app.post("/trips", response_model=TripOut)
def create_trip(trip_data: TripCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    #generate a unique invite code for this trip
    new_trip = Trip(
        name=trip_data.name,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        invite_code=generate_invite_code()
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    #automatically make the creator the Organiser of this trip
    new_membership = Membership(
        user_id=current_user.user_id,
        trip_id=new_trip.trip_id,
        role="Organiser"
    )

    db.add(new_membership)
    db.commit()

    return new_trip

@app.get("/trips/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

#to make sure this user has a memebership of that trip 
    membership = db.query(Membership).filter(
        #find rows where the trip_id column (on the membership table) equals the specific number of trip id e.g. 1
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    return trip

#using patch to update
@app.patch("/trips/{trip_id}", response_model=TripOut)
#using trip create because w are are sending out info in the same structure again
def update_trip(trip_id: int, trip_data: TripCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

#to check that the user and trip id we have match to a member of this trip
    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()
#checking membership before gave us access to their role
    if not membership or membership.role not in ["Organiser", "Co-organiser"]:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this trip")

#now add the new details to trip
    trip.name = trip_data.name
    trip.start_date = trip_data.start_date
    trip.end_date = trip_data.end_date

    db.commit()
    db.refresh(trip)

    return trip

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

#!= for checking one thing 
    if not membership or membership.role != "Organiser":
        raise HTTPException(status_code=403, detail="Only the Organiser can delete this trip")

    db.delete(trip)
    db.commit()

    return {"detail": "Trip deleted successfully"}

@app.get("/trips/{trip_id}/invite")
def get_invite_link(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership or membership.role not in ["Organiser", "Co-organiser"]:
        raise HTTPException(status_code=403, detail="You do not have permission to invite members to this trip")

    return {"invite_code": trip.invite_code}


@app.post("/trips/join/{invite_code}")
#dont need to use a parameter for trip because invite code connects us directly to the specific trip we need 
def join_trip(invite_code: str, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.invite_code == invite_code).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    existing_membership = db.query(Membership).filter(
        Membership.trip_id == trip.trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if existing_membership:
        raise HTTPException(status_code=400, detail="You are already a member of this trip")

#no need to create a memebrship parameter as we arent inputiing new info so we can just use trip and current_user
    new_membership = Membership(
        user_id=current_user.user_id,
        trip_id=trip.trip_id,
        role="Member"
    )

    db.add(new_membership)
    db.commit()

    return {"detail": "Successfully joined trip", "trip_id": trip.trip_id}

@app.delete("/trips/{trip_id}/members/{user_id}")
def remove_member(trip_id: int, user_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    #check the REQUESTER's membership - are they even allowed to remove people?
    requester_membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not requester_membership or requester_membership.role != "Organiser":
        raise HTTPException(status_code=403, detail="Only the Organiser can remove members")

    #now find the TARGET's membership - the person being removed
    target_membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == user_id
    ).first()

    if not target_membership:
        raise HTTPException(status_code=404, detail="This user is not a member of this trip")

    #guard against removing the Organiser themselves
    if target_membership.role == "Organiser":
        raise HTTPException(status_code=400, detail="The Organiser cannot be removed")

    db.delete(target_membership)
    db.commit()

    return {"detail": "Member removed successfully"}


@app.post("/trips/{trip_id}/activities", response_model=ActivityOut)
def create_activity(trip_id: int, activity_data: ActivityCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership or membership.role not in ["Organiser", "Co-organiser"]:
        raise HTTPException(status_code=403, detail="You do not have permission to add activities to this trip")

    new_activity = Activity(
        trip_id=trip_id,
        name=activity_data.name,
        start_time=activity_data.start_time,
        end_time=activity_data.end_time,
        address=activity_data.address,
        cost=activity_data.cost
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity

#if what you are filtering for can have multiple rows sharing the same forgein key digit then use .all/list
#like activity there are several sharing the same trip id diffent from trip, only one trip with a trip id
@app.get("/trips/{trip_id}/activities", response_model=list[ActivityOut])
def get_activities(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    #to make sure this user has a membership of that trip
    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    #get ALL activities belonging to this trip
    activities = db.query(Activity).filter(Activity.trip_id == trip_id).all()

    return activities


@app.post("/trips/{trip_id}/activities/{activity_id}/respond", response_model=ActivityResponseOut)
def create_activity_response(activity_id: int, trip_id: int, activity_response_data: ActivityResponseCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    #check if this user already responded to this activity
    #using foreign keys
    existing_response = db.query(ActivityResponse).filter(
        ActivityResponse.activity_id == activity_id,
        ActivityResponse.user_id == current_user.user_id
    ).first()

    if existing_response:
        #update the existing response instead of creating a new one
        existing_response.status = activity_response_data.status
        db.commit()
        db.refresh(existing_response)
        return existing_response
    else:
        #no response yet - create a new one
        new_response = ActivityResponse(
            user_id=current_user.user_id,
            activity_id=activity_id,
            status=activity_response_data.status
        )
        db.add(new_response)
        db.commit()
        db.refresh(new_response)
        return new_response

@app.get("/trips/{trip_id}/activities/{activity_id}/responses", response_model=list[ActivityResponseOut])
def get_activity_responses(trip_id: int, activity_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    #get everyone's responses to this activity, not just the requester's own
    responses = db.query(ActivityResponse).filter(ActivityResponse.activity_id == activity_id).all()

    return responses

@app.post("/trips/{trip_id}/accommodation", response_model=AccommodationOut)
def create_accommodation(trip_id: int, accommodation_data: AccommodationCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership or membership.role not in ["Organiser", "Co-organiser"]:
        raise HTTPException(status_code=403, detail="You do not have permission to add accommodation to this trip")

    new_accommodation = Accommodation(
        trip_id=trip_id,
        check_in_date=accommodation_data.check_in_date,
        check_out_date=accommodation_data.check_out_date,
        address=accommodation_data.address,
    )

    db.add(new_accommodation)
    db.commit()
    db.refresh(new_accommodation)

    return new_accommodation


@app.get("/trips/{trip_id}/accommodation", response_model=list[AccommodationOut])
def get_accommodation(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    accommodations = db.query(Accommodation).filter(Accommodation.trip_id == trip_id).all()

    return accommodations


@app.get("/trips/{trip_id}/costs")
def get_trip_costs(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    activities = db.query(Activity).filter(Activity.trip_id == trip_id).all()

    #works as an array for loop, with activities as the array
    total_cost = sum(activity.cost for activity in activities if activity.cost is not None)

    return {"trip_id": trip_id, "total_cost": total_cost}

@app.get("/trips/{trip_id}/packing-list")
def get_packing_list(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    activities = db.query(Activity).filter(Activity.trip_id == trip_id).all()
    activity_names = [activity.name for activity in activities]
    activities_text = ", ".join(activity_names) if activity_names else "no specific activities planned yet"

    response = gemini_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"Suggest a packing list for a trip called '{trip.name}', from {trip.start_date} to {trip.end_date}. Planned activities include: {activities_text}. Return just a short bullet list, no extra commentary."
    )

    packing_list = response.text

    return {"trip_id": trip_id, "trip_name": trip.name, "packing_list": packing_list}

@app.get("/trips", response_model=list[TripOut])
def get_my_trips(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    #find all memberships belonging to this user
    memberships = db.query(Membership).filter(Membership.user_id == current_user.user_id).all()

    #pull out the actual trip id for each membership m in memberships
    trip_ids = [membership.trip_id for membership in memberships]
    trips = db.query(Trip).filter(Trip.trip_id.in_(trip_ids)).all()

    return trips

@app.get("/trips/{trip_id}/members", response_model=list[MembershipOut])
def get_trip_members(trip_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    membership = db.query(Membership).filter(
        Membership.trip_id == trip_id,
        Membership.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    memberships = db.query(Membership).filter(Membership.trip_id == trip_id).all()

    return memberships