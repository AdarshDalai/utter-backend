from pydantic import BaseModel

class Notification(BaseModel):
    message: str
    user_id: str
    read: bool