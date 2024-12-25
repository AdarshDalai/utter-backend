from fastapi import APIRouter, HTTPException, Body, Depends, Response
from pydantic import BaseModel
from app.services.auth import get_current_user
from app.services.supabase import create_user, login_user, logout_user, reset_password
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
async def sign_up(request: SignUpRequest, response: Response):
    try:
        auth_response = create_user( User(
            email=request.email,
            fullname=request.fullname,
            username=request.username,
            bio=request.bio,
            profile_picture_url=request.profile_picture_url),
            password=request.password
        )
        access_token = auth_response.session.access_token
        refresh_token = auth_response.session.refresh_token
        response.set_cookie(key="access_token", value = f"Bearer {access_token}", httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return {"message": "User created successfully", "auth_response": auth_response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    try:
        auth_response = login_user(email=request.email, password=request.password)
        access_token = token = auth_response.session.access_token
        refresh_token = auth_response.session.refresh_token
        response.set_cookie(key="access_token", value = f"Bearer {access_token}", httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        return {"message": "User logged in", "session": auth_response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    try:
        auth_response = logout_user()
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset_password")
async def reset_password(email: str, redirect_to: str, current_user: dict = Depends(get_current_user)):
    try:
        auth_response = reset_password(email, redirect_to)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/current_user", tags=["auth"])
def get_current_user_details(current_user: dict = Depends(get_current_user)):
    """
    Endpoint to retrieve the currently authenticated user.
    """
    user = current_user
    return {"user": user}