"""Run this once to delete all uploaded DiviJoyToons videos that violate copyright."""
from dotenv import load_dotenv
from uploader import get_youtube_service

load_dotenv()

def list_my_videos(youtube):
    request = youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        maxResults=50,
    )
    response = request.execute()
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append((video_id, title))
        print(f"Found: [{video_id}] {title}")
    return videos

def delete_video(youtube, video_id, title):
    try:
        youtube.videos().delete(id=video_id).execute()
        print(f"Deleted: [{video_id}] {title}")
    except Exception as e:
        print(f"Failed to delete [{video_id}]: {e}")

def main():
    youtube = get_youtube_service(
        credentials_file="credentials.json",
        token_file="token.json"
    )
    print("Fetching your uploaded videos...")
    videos = list_my_videos(youtube)
    if not videos:
        print("No videos found.")
        return
    print(f"\nFound {len(videos)} video(s). Deleting all...\n")
    for video_id, title in videos:
        delete_video(youtube, video_id, title)
    print("\nAll videos deleted successfully.")

if __name__ == "__main__":
    main()
