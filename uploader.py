from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
import time

# Only youtube.upload scope — avoids invalid_scope error
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

LANG_PLAYLIST_IDS = {
    # Add your playlist IDs here after creating them in YouTube Studio
    # "en": "PLxxxxxxxxxxxxxxx",
    # "hi": "PLxxxxxxxxxxxxxxx",
}

def get_youtube_service(credentials_file="credentials.json", token_file="token.json"):
    creds = None
    token_path = Path(token_file)
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception as e:
            print(f"Token invalid ({e}), deleting and re-authenticating...")
            token_path.unlink()
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_short(youtube, video_path, title, description, tags,
                made_for_kids=True, lang_code="en", retries=2):
    for attempt in range(retries):
        try:
            request = youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": f"{title} #Shorts",
                        "description": description,
                        "tags": tags + ["Shorts", "DiviJoyToons", "KidsRhymes"],
                        "categoryId": "27",
                    },
                    "status": {
                        "privacyStatus": "public",
                        "selfDeclaredMadeForKids": made_for_kids,
                    },
                },
                media_body=MediaFileUpload(video_path, resumable=True),
            )
            response = request.execute()
            video_id = response.get("id", "")
            print(f"  Uploaded: https://youtube.com/watch?v={video_id}")
            return video_id
        except Exception as e:
            err = str(e)
            if "Video Uploads per day" in err or "rateLimitExceeded" in err:
                print(f"  Daily upload quota hit. Video saved locally: {video_path}")
                return None
            elif attempt < retries - 1:
                print(f"  Upload attempt {attempt+1} failed: {e}. Retrying in 30s...")
                time.sleep(30)
            else:
                print(f"  Upload failed: {e}. Video saved locally: {video_path}")
                return None
