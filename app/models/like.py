from pydantic import BaseModel

class Like(BaseModel):
    post_id: str
    user_id: str