from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models import Users
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#key to show it came form our server
SECRET_KEY = "your-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#pulls the token string out of the Authorization header on incoming requests
oauth2_scheme = HTTPBearer()

#method to hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#method to make sure hashed passowrd matches plain password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#method to create a JWT token for a logged-in user
#dict: data type key and value
def create_access_token(data: dict):
    to_encode = data.copy()
    #adds allowed time to time now to get expiry time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    #create the signed token string that acts as proof of identity,
    #instead of having the user sign in repeatedly
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#method to check a request's token is valid decodes it to get sub: email and return the matching user 
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    #unwrap the actual token string from the credentials object
    token = credentials.credentials

    #pre-build the error once, since we may need to raise it from a few places below
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        #reverses jwt.encode - checks signature is valid and not expired
        #as token contains email and exp
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #pulls email
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    #look up the user this token belongs to
    user = db.query(Users).filter(Users.email == email).first()
    if user is None:
        raise credentials_exception

#so this method returns all users details
    return user