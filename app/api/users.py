import os
import time
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.auth import get_current_user
from app.services.supabase import supabase, update_user_bio, update_user_profile_picture, update_user_username, upload_avatar
from app.models.user import User
from app.services.cloudflare import upload_profile_picture_to_r2

router = APIRouter()

@router.get("/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User retrieved", "user": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get a user's posts
@router.get("/{user_id}/posts")
async def get_user_posts(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("posts").select("*").eq("user_id", user_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="No posts found for this user")
        return {"message": "User posts retrieved", "posts": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get followers of a user
@router.get("/{user_id}/followers")
async def get_user_followers(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("followers").select("follower_id").eq("following_id", user_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="No followers found for this user")
        return {"message": "Followers retrieved", "followers": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get users the given user is following
@router.get("/{user_id}/following")
async def get_user_following(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("followers").select("following_id").eq("follower_id", user_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Not following anyone")
        return {"message": "Following retrieved", "following": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get posts liked by the user
@router.get("/{user_id}/likes")
async def get_user_likes(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("likes").select("post_id").eq("user_id", user_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="No likes found for this user")
        return {"message": "Liked posts retrieved", "likes": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/update_username")
async def update_username(username: str, current_user: dict = Depends(get_current_user)):
    try:
        response = update_user_username( username)
        if not response.user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Username updated", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/update_profile_picture")
async def update_profile_picture(profile_picture: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        # Generate a unique file name using user ID and timestamp
        file_extension = profile_picture.filename.split('.')[-1]
        unique_file_name = f"{current_user['sub']}_{int(time.time())}.{file_extension}"
        
        # Save the UploadFile to a temporary file
        temp_file_path = f"/tmp/{unique_file_name}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await profile_picture.read())
        
        # Upload the profile picture to Supabase storage
        upload_response = upload_avatar(temp_file_path, unique_file_name)
        
        if not upload_response:
            raise HTTPException(status_code=400, detail="Failed to upload profile picture.")
        
        # Get the public URL of the uploaded profile picture
        profile_picture_url_response = supabase.storage.from_("profile_pictures").get_public_url(upload_response['full_path'])
        profile_picture_url = profile_picture_url_response.get('publicURL')
        
        if not profile_picture_url:
            raise HTTPException(status_code=400, detail="Failed to get profile picture URL.")
        
        # Update the user's profile picture URL in the database
        response = update_user_profile_picture(profile_picture_url)
        if not response.user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Profile picture updated", "user": response.user}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.put("/update_bio")
async def update_bio( bio: str, current_user: dict = Depends(get_current_user)):
    try:
        response = update_user_bio(bio)
        if not response.user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Bio updated", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/update_name")
async def update_name(name: str, current_user: dict = Depends(get_current_user)):
    try:
        response = update_user_username(name)
        if not response.user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Name Updated", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    
        