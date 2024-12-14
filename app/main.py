from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.posts import router as posts_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(posts_router, prefix="/posts", tags=["posts"])