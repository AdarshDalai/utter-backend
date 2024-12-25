from fastapi import APIRouter, HTTPException, Depends
from app.services.auth import get_current_user
from app.services.supabase import supabase

from app.utils.db import get_db

router = APIRouter()

@router.post("/{target_user_id}", tags=["Follow"])
async def send_follow_request(
    target_user_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Send a follow request to another user.
    If the user's account is private, the request is marked as 'pending'.
    """
    try:
        follower_id = current_user.user.id

        # Check if the target user exists
        target_user_query = supabase.table("profiles").select("id, is_private").eq("id", target_user_id).execute()
        target_user = target_user_query.data
        if not target_user or len(target_user) != 1:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        target_user = target_user[0]  # Extract the single row

        # Determine the follow request status
        status = "pending" if target_user["is_private"] else "accepted"

        # Insert the follow request
        follow_data = {
            "follower_id": follower_id,
            "following_id": target_user_id,
            "status": status
        }
        response = supabase.table("followers").insert(follow_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to send follow request")

        return {"message": "Follow request sent successfully", "status": status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.put("/{follow_request_id}/action", tags=["Follow"])
async def manage_follow_request(
    follow_request_id: int, 
    action: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Accept or reject a follow request.
    - `action` must be 'accept' or 'reject'.
    """
    try:
        if action not in ["accept", "reject"]:
            raise HTTPException(status_code=400, detail="Invalid action")

        # Fetch the follow request
        follow_query = supabase.table("followers").select("*").eq("id", follow_request_id).single().execute()
        follow_request = follow_query.data
        if not follow_request:
            raise HTTPException(status_code=404, detail="Follow request not found")

        # Ensure the current user is the target of the request
        if follow_request["following_id"] != current_user.user.id:
            raise HTTPException(status_code=403, detail="You are not authorized to manage this follow request")

        # Update the status based on the action
        updated_status = "accepted" if action == "accept" else "rejected"
        response = supabase.table("followers").update({"status": updated_status}).eq("id", follow_request_id).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update follow request status")

        return {"message": f"Follow request {action}ed successfully", "status": updated_status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@router.get("/followers", tags=["Follow"])
async def get_followers(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the list of followers for the current user.
    """
    try:
        user_id = current_user.user.id
        query = supabase.table("followers").select("follower_id, profiles!followers_follower_id_fkey(username, profile_picture_url)").eq("following_id", user_id).eq("status", "accepted").execute()

        if not query.data:
            raise HTTPException(status_code=400, detail=query.error.message)

        return {"followers": query.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/following", tags=["Follow"])
async def get_following(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the list of users the current user is following.
    """
    try:
        user_id = current_user.user.id
        query = supabase.table("followers").select("following_id, profiles!followers_following_id_fkey(username, profile_picture_url)").eq("follower_id", user_id).eq("status", "accepted").execute()

        if not query:
            raise HTTPException(status_code=400, detail=query.error.message)

        return {"following": query.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@router.delete("/unfollow/{target_user_id}", tags=["Follow"])
async def unfollow_user(
    target_user_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Unfollow a user.
    """
    try:
        follower_id = current_user.user.id

        # Delete the follow relationship
        response = (
            supabase.table("followers")
            .delete()
            .eq("follower_id", follower_id)
            .eq("following_id", target_user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to unfollow user")

        return {"message": "Successfully unfollowed the user"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
