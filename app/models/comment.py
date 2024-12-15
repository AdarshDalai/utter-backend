from pydantic import BaseModel

class Comment(BaseModel):
    content: str
    post_id: str
    user_id: str