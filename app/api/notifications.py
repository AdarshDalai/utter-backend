from fastapi import APIRouter, Depends, HTTPException
from app.services.supabase import get_current_user, supabase
from app.models.notification import Notification
from app.utils.db import get_db

router = APIRouter()

@router.post("/create_notification")
async def create_notification(notification: Notification):
    try:
        response = supabase.table("notifications").insert({
            "message": notification.message,
            "user_id": notification.user_id,
            "read": notification.read,
        }).execute()
        return {"message": "Notification created successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/notifications/{user_id}")
async def get_notifications(user_id: str):
    try:
        response = supabase.table("notifications").select("*").eq("user_id", user_id).execute()
        return {"message": "Notifications retrieved", "notifications": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
