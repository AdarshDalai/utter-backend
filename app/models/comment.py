from typing import Optional
from pydantic import BaseModel

class Comment(BaseModel):
    id: int
    post_id: int
    user_id: str
    comment: str
    parent_id: Optional[int]
    created_at: str