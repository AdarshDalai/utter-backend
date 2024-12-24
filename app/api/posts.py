from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.supabase import supabase
from app.models.post import Post
from app.models.user import User
from app.services.cloudflare import upload_posts_to_r2
from app.services.supabase import get_current_user
from app.utils.db import get_db

router = APIRouter()

@router.post("/post", response_model=Post)
async def create_post(
    content: str, 
    media: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint to create a new post with media upload.
    - Accepts `content` (caption) and `media` (file).
    - Retrieves `user_id` from the token.
    """
    try:
        # Step 1: Upload media to Cloudflare (or another media storage)
        media_url = await upload_posts_to_r2(media, media.filename)  # Assuming this function uploads the file and returns the URL
        
        # Step 2: Insert post data into Supabase database
        post_data = {
            "content": content,
            "media_url": media_url,
            "user_id": current_user.user.id  # Get the authenticated user ID
        }
        response = supabase.table("posts").insert(post_data).execute()

        # Check if insertion was successful
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create post")

        # Step 3: Return the created post data
        return response.data[0]  # Return the first post record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")