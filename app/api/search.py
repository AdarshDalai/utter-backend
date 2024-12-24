from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.services.supabase import supabase, get_current_user
from app.models.user import User
from sqlalchemy.sql import text
import fuzzywuzzy
from fuzzywuzzy import fuzz

router = APIRouter()

@router.get("/search_users", response_model=List[User], tags=["Search"])
async def search_users(query: str, current_user: dict = Depends(get_current_user)):
    """
    Search for users based on their name or username.
    Provides:
    - Exact matches (username or full name starts with search query).
    - Partial matches (username or full name contains search query).
    - Popular matches (prioritizes users with more followers).
    - Fuzzy matches (handles slight typos or variations).
    """
    try:
        # Step 1: Search for exact and partial matches using SQL query
        query_sql = (
            supabase.table("profiles")
            .select("id, username, fullname, profile_picture_url, followers_count")
            .ilike("username", f"%{query}%")  # Partial match for username
            .or_("ilike(fullname, '%{query}%')")  # Partial match for full name
            .execute()
        )

        if not query_sql.data:
            raise HTTPException(status_code=404, detail="No users found")

        # Step 2: Rank users by relevance
        users = query_sql.data

        # Fuzzy match the query against the usernames and full names of the users
        # Rank by fuzzy score (adjust threshold to fit your case)
        ranked_users = []
        for user in users:
            username_score = fuzz.partial_ratio(query.lower(), user["username"].lower())
            fullname_score = fuzz.partial_ratio(query.lower(), user["fullname"].lower())
            score = max(username_score, fullname_score)

            ranked_users.append({
                **user,
                "score": score  # Add the score for ranking
            })

        # Step 3: Sort users by score (high score first) and then by popularity (followers count)
        ranked_users.sort(key=lambda x: (x["score"], x["followers_count"]), reverse=True)

        # Step 4: Return ranked list of users
        return ranked_users

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")