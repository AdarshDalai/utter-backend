from pydantic import BaseModel
from typing import Optional

class Post(BaseModel):
    id: int
    content: str
    media_url: str = None
    user_id: str
    created_at:str