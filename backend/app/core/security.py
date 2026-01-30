import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

# this module handles the password encryption and jwt tokens

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("HASH_ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "0"))

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Using argon2 here
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None) -> str:
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Define what goes INSIDE the token
    to_encode = {
        "sub": str(subject), # The User ID or Email
        "role": role,        # We add the role so the frontend knows who logged in
        "exp": expire        # Expiration time
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt