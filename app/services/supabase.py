import os
from supabase import create_client, Client
from passlib.context import CryptContext


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_user(email: str, password: str, username: str, bio: str, profile_picture_url: str):
    password_hash = hash_password(password)
    
    # Insert user data with the hashed password
    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
    })
    
    user_data = {
        "email": email,
        "username": username,
        "bio": bio,
        "profile_picture_url": profile_picture_url,
        "password_hash": password_hash,  # Save the hashed password
    }

    user_table = supabase.table("users")
    user_table.insert(user_data).execute()

    return response

def get_user_by_email(email: str):
    return supabase.auth.api.get_user(email)

def login_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })

def logout_user():
    return supabase.auth.sign_out()

def reset_password(email: str, redirect_to: str):
    return supabase.auth.reset_password_for_email(email, {
        "redirect_to": redirect_to,
    })

def get_session():
    return supabase.auth.get_session()

def update_user(user_id: str, updates: dict):
    return supabase.table("users").update(updates).eq("id", user_id).execute()