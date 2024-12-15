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
    # Hash the password
    password_hash = hash_password(password)
    
    # Sign up the user in auth.users and capture their ID
    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "username": username,
                "bio": bio,
                "profile_picture_url": profile_picture_url,
                "password_hash": password_hash
            }
        }
    })

    # Extract the user ID from the response
    #user_id = response.get("user", {}).get("id")
    #if not user_id:
    #   raise ValueError("Failed to create user: User ID not returned from auth.sign_up")

    # Prepare the user data to insert into the users table
    # user_data = {
    #     "id": user_id,  # Use the ID from auth.users
    #     "email": email,
    #     "username": username,
    #     "bio": bio,
    #     "profile_picture_url": profile_picture_url,
    #     "password_hash": password_hash,  # Save the hashed password
    # }

    # Insert the data into the users table
    #insert_response = supabase.table("users").insert(user_data).execute()

    return {
        "auth_response": response,
    #    "insert_response": insert_response
    }

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

def get_current_user():
    return supabase.auth.get_user()