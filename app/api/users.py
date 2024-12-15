from fastapi import APIRouter, HTTPException
from app.services.supabase import supabase
from app.models.user import User
from app.services.supabase import update_user
from app.services.cloudflare import upload_profile_picture_to_r2

router = APIRouter()

@router.get("/{user_id}")
async def get_user(user_id: str):
    try:
        response = supabase.table("profiles").select("username, bio, profile_picture_url, created_at, is_private").eq("id", user_id).execute()
        return {"message": "User retrieved", "user": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("update/{user_id}")
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

@router.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    # Query user profile information, their posts, followers/following, likes, and comments
    response = supabase.table("profiles").select("*").eq("id", user_id).execute()

    if response.get('data') is None or len(response['data']) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return response['data'][0]


@router.get("/{user_id}/posts")
async def get_user_posts(user_id: str):
    # Get posts of the user
    response = supabase.table("posts").select("""
        id, content, media_url, created_at,
        likes(user_id),
        comments(user_id, comment, created_at)
    """).eq("user_id", user_id).execute()

    if response.get('data') is None or len(response['data']) == 0:
        raise HTTPException(status_code=404, detail="No posts found for this user")
    
    return response['data']


@router.get("/user/{user_id}/followers")
async def get_user_followers(user_id: str):
    # Get followers of the user
    response = supabase.table("followers").select("follower_id").eq("following_id", user_id).execute()
    
    if response.get('data') is None or len(response['data']) == 0:
        raise HTTPException(status_code=404, detail="No followers found for this user")
    
    return response['data']


@router.get("/user/{user_id}/following")
async def get_user_following(user_id: str):
    # Get users the given user is following
    response = supabase.table("followers").select("following_id").eq("follower_id", user_id).execute()
    
    if response.get('data') is None or len(response['data']) == 0:
        raise HTTPException(status_code=404, detail="Not following anyone")
    
    return response['data']


@router.get("/user/{user_id}/likes")
async def get_user_likes(user_id: str):
    # Get posts liked by the user
    response = supabase.table("likes").select("post_id").eq("user_id", user_id).execute()

    if response.get('data') is None or len(response['data']) == 0:
        raise HTTPException(status_code=404, detail="No likes found for this user")
    
    return response['data']