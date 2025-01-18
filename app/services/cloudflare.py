import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile

# Load environment variables
load_dotenv()

# Configuration variables
AccountID = os.getenv("CLOUDFLARE_R2_ID")
Bucket = os.getenv("CLOUDFLARE_R2_BUCKET")
ClientAccessKey = os.getenv("CLOUDFLARE_R2_ACCESS_KEY")
ClientSecret = os.getenv("CLOUDFLARE_R2_SECRET_KEY")
region = os.getenv("CLOUDFLARE_R2_REGION")

ConnectionUrl = f"https://{AccountID}.r2.cloudflarestorage.com"

# Create S3 client for Cloudflare R2
S3Connect = boto3.client(
    's3',
    endpoint_url=ConnectionUrl,
    aws_access_key_id=ClientAccessKey,
    aws_secret_access_key=ClientSecret,
    config=Config(signature_version='s3v4'),
    region_name=region
)


async def upload_to_r2(file: UploadFile, folder: str, file_name: str):
    """
    Upload a file to a specific folder in Cloudflare R2.
    
    :param file: The uploaded file object.
    :param folder: The target folder in the bucket (e.g., "posts", "profile pictures").
    :param file_name: The name to save the file as.
    :return: The public URL of the uploaded file.
    """
    file_content = await file.read()  # Read file content

    try:
        # Check if the file already exists
        file_key = f"{folder}/{file_name}"
        try:
            S3Connect.head_object(Bucket=Bucket, Key=file_key)
            # If exists, delete the old file
            S3Connect.delete_object(Bucket=Bucket, Key=file_key)
        except S3Connect.exceptions.ClientError as e:
            # If the error is a 404 Not Found, ignore it
            if e.response['Error']['Code'] == '404':
                pass
            else:
                raise

        # Upload the file
        S3Connect.put_object(
            Bucket=Bucket,
            Key=file_key,
            Body=file_content,
            ACL="public-read"  # Make the file publicly accessible
        )

        # Return the public URL
        return f"https://pub-6920a900fc98444dbeda48c0377125d5.r2.dev/{file_key}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    
async def upload_posts_to_r2(file: UploadFile, file_name: str):
    """
    Upload a post media file to R2.
    """
    return await upload_file(file, "posts", file_name)


async def upload_profile_picture_to_r2(file: UploadFile, file_name: str):
    """
    Upload a profile picture to R2.
    """
    return await upload_file(file, "profile_pictures", file_name)

def upload_file(file_name, bucket_name, object_name:str):
    if object_name is None:
        object_name = file_name
 
    try:
        S3Connect.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        print(f"An error occurred: {e}")
        return False
    return True