from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from app.models import User
from app.core.database import get_session
from app.core.security import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone

# this tells FastAPI that the token is in the "Authorization: Bearer <token>" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# get current user performs some basic checks and gets the user from the db 
# get current user is called within all the other functions where we need to check a user's credentials
# for example in customers.py current_user depends on this function 
# this function is called when get_customer_profile is called, providing the user object
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
    ) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # checking token:
    # jwt.decode automatically checks the expiration time of the token
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # gets the user from the db
    user = session.get(User, user_id)
    
    if user is None:
        raise credentials_exception
        
    return user # returns the user
