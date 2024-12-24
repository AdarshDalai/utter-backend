from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.services.supabase import supabase, get_current_user
from app.models.post import Post  # Assuming the Post model is defined similarly

router = APIRouter()

@router.get("/", response_model=List[Post], tags=["Feed"])
async def get_feed(current_user: dict = Depends(get_current_user)):
    """
    Fetch the user's feed based on the users they are following.
    - Includes posts from followed users.
    - Orders posts by creation date (most recent first).
    """
    try:
        user_id = current_user.user.id  # Get the current authenticated user

        # Step 1: Get the list of users the current user is following
        followers_query = (
            supabase.table("followers")
            .select("following_id")
            .eq("follower_id", user_id)  # Get the users that the current user is following
            .eq("status", "accepted")  # Ensure the follow status is accepted
            .execute()
        )
        
        # If the user is not following anyone, return an empty feed
        if not followers_query.data:
            return {"posts": []}

        following_ids = [follower["following_id"] for follower in followers_query.data]

        # Step 2: Fetch posts from followed users
        posts_query = (
            supabase.table("posts")
            .select("id, content, media_url, user_id, created_at")
            .in_("user_id", following_ids)  # Get posts from users in the following list
            .order("created_at", desc=True)  # Sort by creation date, descending (most recent first)
            .execute()
        )
        
        # If no posts found, return an empty list
        if not posts_query.data:
            return {"posts": []}

        # Step 3: Return the posts in the feed
        return {"posts": posts_query.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")