from fastapi import APIRouter, HTTPException
from app.services.supabase import supabase
from app.models.comment import Comment

router = APIRouter()

@router.post("/create_comment")
async def create_comment(comment: Comment):
    try:
        response = supabase.table("comments").insert({
            "content": comment.content,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
        }).execute()
        return {"message": "Comment created successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/comments/{post_id}")
async def get_comments(post_id: str):
    try:
        response = supabase.table("comments").select("*").eq("post_id", post_id).execute()
        return {"message": "Comments retrieved", "comments": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))