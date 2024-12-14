from fastapi import APIRouter, HTTPException
from app.services.supabase import supabase
from app.models.post import Post
from app.models.user import User

router = APIRouter()

@router.post("/create_post")
async def create_post(post: Post):
    try:
        response = supabase.table("posts").insert({
            "content": post.content,
            "media_url": post.media_url,
            "user_id": post.user_id,
        }).execute()
        return {"message": "Post created successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feed/{user_id}")
async def get_feed(user_id: str):
    try:
        response = supabase.table("posts").select("*").eq("user_id", user_id).execute()
        return {"message": "Feed retrieved", "posts": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))