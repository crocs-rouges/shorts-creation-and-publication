import os
import google.auth
import google.oauth2.credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime

# OAuth 2.0 scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Path to the YouTube folder containing credentials
YOUTUBE_DIR : str = "cookies/"

# Authentification via OAuth 2.0
def authenticate():
    credentials = None
    # Check if token already exists
    token_path = os.path.join(YOUTUBE_DIR, "token.json")
    client_secret_path = os.path.join(YOUTUBE_DIR, "client_secret.json")
    
    # Verify if a token already exists
    if os.path.exists(token_path):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials, authenticate and save a new token
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Save credentials for next execution
        with open(token_path, "w") as token:
            token.write(credentials.to_json())

    return credentials

# Function to upload video
def upload_youtube(file_path, title, description, tags, category_id, scheduled_time : datetime):
    credentials = authenticate()
    youtube = build("youtube", "v3", credentials=credentials)

    # Video metadata
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "private",  # Upload as private before publishing
            "publishAt": scheduled_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "selfDeclaredMadeForKids": False
        }
    }

    # Upload the video
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    
    print("Upload completed.")
    print(f"Video available at: https://www.youtube.com/watch?v={response['id']}")