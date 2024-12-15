from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.users import router as users_router
from app.api.comments import router as comments_router
from app.api.likes import router as likes_router
from app.api.notifications import router as notifications_router
from app.api.feeds import router as feeds_router
from app.api.follows import router as follows_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(comments_router, prefix="/comments", tags=["comments"])
app.include_router(likes_router, prefix="/likes", tags=["likes"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(feeds_router, tags=["Feed"], prefix="/feed")
app.include_router(follows_router, tags=["Follow"], prefix="/follow")