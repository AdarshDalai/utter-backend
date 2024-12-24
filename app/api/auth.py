from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from app.services.supabase import create_user, login_user, logout_user, reset_password, get_current_user
from app.models.user import User


router = APIRouter()

class SignUpRequest(BaseModel):
    email: str
    password: str
    fullname:str
    username: str
    bio: str
    profile_picture_url: str

@router.post("/signup")
async def sign_up(request: SignUpRequest):
    try:
        response = create_user( User(
            email=request.email,
            fullname=request.fullname,
            username=request.username,
            bio=request.bio,
            profile_picture_url=request.profile_picture_url),
            password=request.password
        )
        return {"message": "User created successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    try:
        response = login_user(email=request.email, password=request.password)
        return {"message": "User logged in", "session": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout():
    try:
        response = logout_user()
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset_password")
async def reset_password(email: str, redirect_to: str):
    try:
        response = reset_password(email, redirect_to)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/current_user", tags=["auth"])
def get_current_user_details(current_user: dict = Depends(get_current_user)):
    """
    Endpoint to retrieve the currently authenticated user.
    """

    return {"user": current_user}