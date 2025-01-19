import time
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi import Body
from app.services.auth import get_current_user
from app.services.supabase import supabase, upload_post
from app.models.post import Post
from app.models.user import User

router = APIRouter()

@router.post("/post", response_model=Post)
async def create_post(
    caption: str = Body(..., embed=True),
    media: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint to create a new post with media upload.
    - Accepts `caption` as JSON and `media` (file).
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
        
        # Step 3: Save the UploadFile to a temporary file
        temp_file_path = f"/tmp/{unique_file_name}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await media.read())
        
        # Step 4: Upload media to Supabase storage
        upload_response = upload_post(temp_file_path, unique_file_name)
        
        if not upload_response:
            raise HTTPException(status_code=400, detail="Failed to upload media.")
        
        # Get the public URL of the uploaded media
        media_url_response = supabase.storage.from_("posts").get_public_url(upload_response['full_path'])
        media_url = media_url_response.get('publicURL')
        
        if not media_url:
            raise HTTPException(status_code=400, detail="Failed to get media URL.")
        
        # Step 5: Insert post data into Supabase
        post_data = {
            "content": caption,
            "media_url": media_url,
            "user_id": current_user["sub"] # Use authenticated user ID
        }
        response = supabase.table("posts").insert(post_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create post.")

        # Step 6: Return the created post
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)