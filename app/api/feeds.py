from fastapi import APIRouter, Depends, HTTPException
from app.services.supabase import supabase
from app.services.supabase import get_current_user

router = APIRouter()

@router.get("/feed", tags=["Feed"])
async def get_feed(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Fetch the feed for the authenticated user.
    Includes posts by users the current user follows.
    """
    try:
        user_id = current_user["user"]["id"]

        # Fetch posts from followed users
        query = (
            supabase.table("posts")
            .select("""
                id,
                content,
                media_url,
                created_at,
                user_id,
                profiles(username, profile_picture_url),
                likes(count) as like_count,
                comments(count) as comment_count
            """)
            .join("followers", "followers.following_id = posts.user_id")
            .eq("followers.follower_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .offset(offset)
            .execute()
        )

        # Check if data exists
        if query.get("data") is None or len(query["data"]) == 0:
            return {"message": "No posts available in the feed", "posts": []}

        return {"message": "Feed retrieved successfully", "posts": query["data"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feed: {str(e)}")