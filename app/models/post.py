from pydantic import BaseModel
from typing import Optional

class Post(BaseModel):
    content: str
    media_url: str = None
    user_id: str