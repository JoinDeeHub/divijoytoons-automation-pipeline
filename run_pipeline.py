from dotenv import load_dotenv
import os
from trend_finder import get_trending_kids_topics
from script_generator import generate_kids_script
from voice_generator import generate_all_languages
from video_creator import create_short_video
from uploader import get_youtube_service, upload_short
import re

load_dotenv()

def sanitize(text):
    return re.sub(r"[^a-zA-Z0-9_]", "_", text)[:30]

def run():
    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    credentials_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "credentials.json")

    print("Step 1: Finding trending topic...")
    topics = get_trending_kids_topics(youtube_api_key, max_results=1)
    if not topics:
        print("No topics found. Exiting.")
        return
    topic = topics[0]
    print(f"Topic: {topic}")

    print("Step 2: Generating script...")
    script = generate_kids_script(gemini_api_key, topic, language="English")
    title = script.get("title", "DiviJoyToons")
    lyrics = script.get("lyrics", "Hello kids!")
    tags = [t.strip() for t in script.get("tags", "").split(",")]
    print(f"Title: {title}")

    base = sanitize(title)

    print("Step 3: Generating voices in all languages...")
    audio_files = generate_all_languages(lyrics, base)

    print("Step 4: Creating videos...")
    youtube = get_youtube_service(credentials_file=credentials_file)
    for idx, (lang_code, audio_path) in enumerate(audio_files.items()):
        video_path = f"output/videos/{base}_{lang_code}.mp4"
        create_short_video(title, lyrics, audio_path, video_path, color_index=idx)

        print(f"Step 5: Uploading {lang_code} video...")
        upload_short(
            youtube=youtube,
            video_path=video_path,
            title=f"{title} ({lang_code.upper()})",
            description=f"DiviJoyToons | Educational Kids Short | {lang_code.upper()}",
            tags=tags,
            made_for_kids=True,
        )

    print("Pipeline complete!")

if __name__ == "__main__":
    run()
