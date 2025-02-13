from fastapi import APIRouter, Depends, HTTPException
from app.services.supabase import supabase
from app.services.auth import get_current_user
from app.utils.db import get_db

router = APIRouter()

@router.post("/like_post")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("likes").insert({
            "post_id": post_id,
            "user_id": current_user["sub"]
        }).execute()
        return {"message": "Post liked successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/unlike_post")
async def unlike_post(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Delete the like entry from the "likes" table
        response = supabase.table("likes").delete().eq("post_id", post_id).eq("user_id", current_user["sub"]).execute()
        
        if response.status_code == 200:
            return {"message": "Post unliked successfully"}
        else:
            raise HTTPException(status_code=404, detail="Like not found or already removed")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/likes/{post_id}")
async def get_likes(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("likes").select("*").eq("post_id", post_id).execute()
        return {"message": "Likes retrieved", "likes": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
