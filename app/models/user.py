from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    fullname:str
    username: str
    bio: str
    profile_picture_url: str = None
    is_private: bool = False