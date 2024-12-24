from dataplane import s3_upload
import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv
import json

from fastapi import HTTPException, UploadFile


load_dotenv()


# 1. Account ID
AccountID = os.environ["CLOUDFLARE_R2_ID"]

# 2. Bucket name
Bucket = os.environ["CLOUDFLARE_R2_BUCKET"]

# 3. Client access key
ClientAccessKey = os.environ["CLOUDFLARE_R2_ACCESS_KEY"]

# 4. Client secret
ClientSecret = os.environ["CLOUDFLARE_R2_SECRET_KEY"]

# 5. Connection url
ConnectionUrl = f"https://{AccountID}.r2.cloudflarestorage.com"

region = os.environ["CLOUDFLARE_R2_REGION"]

# Create a client to connect to Cloudflare's R2 Storage
S3Connect = boto3.client(
    's3',
    endpoint_url=ConnectionUrl,
    aws_access_key_id=ClientAccessKey,
    aws_secret_access_key=ClientSecret,
    config=Config(signature_version='s3v4'),
    region_name=region
)

async def upload_posts_to_r2(file: UploadFile, file_name):

    file_content = await file.read()  # Read the file's content

    try:
        s3_upload(
            S3Client=S3Connect,
            Bucket=Bucket,
            TargetFilePath=f"posts/{file_name}",
            UploadObject=file_content,
            UploadMethod="Object"
        )
        return f"https://{Bucket}.{ConnectionUrl}/posts/{file_name}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    
async def upload_profile_picture_to_r2(file: UploadFile, file_name):
    
    file_content = await file.read()  # Read the file's content

    try:
        s3_upload(
            S3Client=S3Connect,
            Bucket=Bucket,
            TargetFilePath=f"profile pictures/{file_name}",
            UploadObject=file_content,
            UploadMethod="Object"  # Set file to be publicly accessible
        )
        return f"https://{Bucket}.{ConnectionUrl}/profile pictures/{file_name}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")