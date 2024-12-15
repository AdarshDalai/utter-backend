from fastapi import APIRouter, HTTPException
from app.services.supabase import supabase
from app.models.user import User
from app.services.supabase import update_user
from app.services.cloudflare import upload_profile_picture_to_r2

router = APIRouter()

@router.get("/{user_id}")
async def get_user(user_id: str):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return {"message": "User retrieved", "user": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}")
async def update_user_profile(user_id: str, user: User):
    try:
        updated_data = {
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "profile_picture_url": user.profile_picture_url,
        }
        response = update_user(user_id, updated_data)
        return {"message": "User profile updated", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))