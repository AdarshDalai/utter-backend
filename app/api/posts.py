import time
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.auth import get_current_user
from app.services.supabase import supabase
from app.models.post import Post
from app.models.user import User
from app.services.cloudflare import upload_posts_to_r2

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
        # Step 1: Validate input
        if not media:
            raise HTTPException(status_code=400, detail="Media file is required.")
        
        # Step 2: Upload media to Cloudflare R2
        file_extension = media.filename.split('.')[-1]  # Get file extension
        if file_extension.lower() not in ["jpg", "jpeg", "png", "mp4", "mov"]:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        
        # Generate a unique file name using user ID and timestamp
        unique_file_name = f"{current_user['sub']}_{int(time.time())}.{file_extension}"
        media_url = await upload_posts_to_r2(media, unique_file_name)
        
        # Step 3: Insert post data into Supabase
        post_data = {
            "content": content,
            "media_url": media_url,
            "user_id": current_user["sub"] # Use authenticated user ID
        }
        response = supabase.table("posts").insert(post_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create post.")

        # Step 4: Return the created post
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")