import time
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.auth import get_current_user
from app.services.supabase import supabase, upload_post,url
from app.models.post import Post
from app.models.user import User

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
        
        # Step 2: Validate file extension
        file_extension = media.filename.split('.')[-1]  # Get file extension
        if file_extension.lower() not in ["jpg", "jpeg", "png", "mp4", "mov"]:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        
        # Generate a unique file name using user ID and timestamp
        unique_file_name = f"{current_user['sub']}_{int(time.time())}.{file_extension}"
        
        # Step 3: Upload media to Supabase storage
        file_path = f"/tmp/{unique_file_name}"
        with open(file_path, "wb") as buffer:
            buffer.write(await media.read())
        
        upload_response = upload_post(file_path, unique_file_name)
        
        if not upload_response:
            raise HTTPException(status_code=400, detail="Failed to upload media.")
        
        media_url = f"{url}/storage/v1/object/public/posts/{unique_file_name}"
        
        # Step 4: Insert post data into Supabase
        post_data = {
            "content": content,
            "media_url": media_url,
            "user_id": current_user["sub"] # Use authenticated user ID
        }
        response = supabase.table("posts").insert(post_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create post.")

        # Step 5: Return the created post
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")