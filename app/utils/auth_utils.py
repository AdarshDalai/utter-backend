import os
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT Secret and Algorithm (these should match your Supabase settings)
SECRET_KEY = os.getenv("SUPABASE_JWT_SECRET")  # Supabase JWT Secret Key
ALGORITHM = "HS256"

# Security scheme for FastAPI
security = HTTPBearer()

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Retrieve the currently logged-in user from the Authorization header.
    """
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")  # Supabase user ID from the "sub" claim

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return user_id