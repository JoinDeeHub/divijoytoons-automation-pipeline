from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
import time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

LANG_PLAYLIST_IDS = {
    # Fill these after creating playlists on your channel
    # "en": "PLxxxxxxxxxxxxxxx",
    # "hi": "PLxxxxxxxxxxxxxxx",
}

def get_youtube_service(credentials_file="credentials.json", token_file="token.json"):
    creds = None
    token_path = Path(token_file)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_short(youtube, video_path, title, description, tags,
                made_for_kids=True, lang_code="en", retries=3):
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
            print(f"Uploaded: https://youtube.com/watch?v={video_id}")

            # Add to language playlist if configured
            playlist_id = LANG_PLAYLIST_IDS.get(lang_code)
            if playlist_id:
                add_to_playlist(youtube, video_id, playlist_id)

            return video_id
        except Exception as e:
            err = str(e)
            if "Video Uploads per day" in err or "rateLimitExceeded" in err:
                print(f"Daily upload quota hit. Waiting 60s before retry {attempt+1}/{retries}...")
                time.sleep(60)
            else:
                raise
    print(f"Upload failed after {retries} retries. Video saved locally: {video_path}")
    return None

def add_to_playlist(youtube, video_id, playlist_id):
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }}
        ).execute()
        print(f"Added to playlist: {playlist_id}")
    except Exception as e:
        print(f"Playlist add failed: {e}")
