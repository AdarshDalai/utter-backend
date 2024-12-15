from pydantic import BaseModel

class User(BaseModel):
    email: str
    username: str
    bio: str
    profile_picture_url: str