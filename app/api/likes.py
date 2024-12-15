from fastapi import APIRouter, HTTPException
from app.services.supabase import supabase

router = APIRouter()

@router.post("/like_post")
async def like_post(post_id: str, user_id: str):
    try:
        response = supabase.table("likes").insert({
            "post_id": post_id,
            "user_id": user_id,
        }).execute()
        return {"message": "Post liked successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/likes/{post_id}")
async def get_likes(post_id: str):
    try:
        response = supabase.table("likes").select("*").eq("post_id", post_id).execute()
        return {"message": "Likes retrieved", "likes": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))