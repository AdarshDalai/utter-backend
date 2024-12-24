import os
from supabase import create_client, Client
from app.models.user import User


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def create_user(user: User, password: str):
        
    # Sign up the user in auth.users and capture their ID
    response = supabase.auth.sign_up({
        "email": user.email,
        "password": password,
        "options": {
            "data": {
                "name": user.fullname,
                "username": user.username,
                "bio": user.bio,
                "profile_picture_url": user.profile_picture_url
            }
        }
    })

    return {
        "auth_response": response
    }

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

def update_user_username(username: str):
    return supabase.auth.update_user( {
        "data" : {
            "username": username
        }
    })

def update_user_profile_picture(profile_picture_url: str):
    return supabase.auth.update_user( {
        "data" : {
            "profile_picture_url": profile_picture_url
        }
    })

def update_user_bio(bio: str):
    return supabase.auth.update_user( {
        "data" : {
            "bio": bio
        }
    })

def get_current_user():
    return supabase.auth.get_user()

def update_user_name(fullname: str):
    return supabase.auth.update_user(
        {
            "data" : {
                "name" : fullname
            }
        }
    )
