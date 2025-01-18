import os
from fastapi import UploadFile
from supabase import create_client, Client
from app.models.user import User


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def create_user(user: User, password: str):
        
    # Sign up the user in auth.users and capture their ID
    return supabase.auth.sign_up({
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

def get_current_user(token:str):
    return supabase.auth.get_user(token)

def update_user_name(fullname: str):
    return supabase.auth.update_user(
        {
            "data" : {
                "name" : fullname
            }
        }
    )

def refresh_token(token: str) :
    return supabase.auth.refresh_session(token)
    
def search_name_or_username(text: str):
    response = supabase.table("profiles").select("id, username, name, profile_picture_url").or_(f"name.eq.%{text}%,username.eq.%{text}%").execute()

def upload_post(file_path: str, file_name: str):
    with open(file_path, 'rb') as f:
        response = supabase.storage.from_("posts").upload(
            file=f,
            path=file_name,
            file_options={"cache-control": "3600", "upsert": "false"},
        )
    return response

def delete_post(file_name: str):
    response = supabase.storage.from_("posts").remove([file_name])
    return response

def upload_avatar(file_path: str, file_name: str):
    with open(file_path, 'rb') as f:
        response = supabase.storage.from_("profile_pictures").upload(
            file=f,
            path=file_name,
            file_options={"cache-control": "3600", "upsert": "false"},
        )
    return response

def replace_avatar(file_path: str, file_name: str):
    with open(file_path, 'rb') as f:
        response = supabase.storage.from_("profile_pictures").update(
            file=f,
            path=file_name,
            file_options={"cache-control": "3600", "upsert": "true"},
        )
    return response

def delete_avatar(file_name: str):
    response = supabase.storage.from_("profile_pictures").remove([file_name])
    return response