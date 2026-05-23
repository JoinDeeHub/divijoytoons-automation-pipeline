"""Run this once to delete all uploaded DiviJoyToons videos."""
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path
import os

load_dotenv()

# Full scopes needed for list + delete
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

def get_youtube_full(credentials_file="credentials.json", token_file="token_delete.json"):
    creds = None
    token_path = Path(token_file)
    # Always delete old token to force fresh auth with new scopes
    if token_path.exists():
        token_path.unlink()
        print("Old token removed, re-authenticating with full scopes...")
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def list_my_videos(youtube):
    request = youtube.channels().list(part="contentDetails", mine=True)
    response = request.execute()
    uploads_playlist = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos = []
    next_page = None
    while True:
        pl_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=50,
            pageToken=next_page,
        )
        pl_response = pl_request.execute()
        for item in pl_response.get("items", []):
            video_id = item["snippet"]["resourceId"]["videoId"]
            title = item["snippet"]["title"]
            videos.append((video_id, title))
            print(f"  Found: [{video_id}] {title}")
        next_page = pl_response.get("nextPageToken")
        if not next_page:
            break
    return videos

def delete_video(youtube, video_id, title):
    try:
        youtube.videos().delete(id=video_id).execute()
        print(f"  Deleted: [{video_id}] {title}")
    except Exception as e:
        print(f"  Failed [{video_id}]: {e}")

def main():
    credentials_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "credentials.json")
    youtube = get_youtube_full(credentials_file=credentials_file)
    print("\nFetching your uploaded videos...")
    videos = list_my_videos(youtube)
    if not videos:
        print("No videos found on your channel.")
        return
    print(f"\nFound {len(videos)} video(s). Deleting all...\n")
    for video_id, title in videos:
        delete_video(youtube, video_id, title)
    print("\nAll videos deleted successfully.")

if __name__ == "__main__":
    main()
