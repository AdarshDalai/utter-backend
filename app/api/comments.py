from pydantic import BaseModel
from app.models.comment import Comment
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.services.supabase import get_current_user, supabase

router = APIRouter()

class CommentCreate(BaseModel):
    comment: str
    post_id: int
    parent_id: Optional[int] = None  # For replies

@router.post("/create_comment", response_model=Comment)
async def create_comment(
    comment: str,
    post_id: int,
    parent_id: Optional[int] = None,  # Optional parent ID for replies
    current_user: dict = Depends(get_current_user)
):
    """
    Create a comment or reply.
    - Accepts `comment` (text), `post_id` (post to comment on), and optional `parent_id` (if it's a reply).
    - Retrieves `user_id` from the authenticated user.
    """
    try:
        # Step 1: Prepare the comment data
        comment_data = {
            "comment": comment,
            "post_id": post_id,
            "user_id": current_user.user.id,  # Authenticated user ID
            "parent_id": parent_id  # Optional parent ID for replies
        }

        # Step 2: Insert comment into Supabase
        response = supabase.table("comments").insert(comment_data).execute()

        # Check if insertion was successful
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create comment")

        # Step 3: Return the created comment data
        return Comment(**response.data[0])  # Map response data to Comment model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")