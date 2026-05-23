from dotenv import load_dotenv
import os
from trend_finder import get_trending_kids_topics
from script_generator import generate_kids_script
from voice_generator import generate_all_languages
from translator import translate_all_languages
from video_creator import create_short_video
from uploader import get_youtube_service, upload_short
import re

load_dotenv()

def sanitize(text):
    return re.sub(r"[^a-zA-Z0-9_]", "_", text)[:30]

def run():
    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
    gemini_api_key  = os.getenv("GEMINI_API_KEY", "")
    credentials_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "credentials.json")

    print("Step 1: Finding trending topic...")
    topics = get_trending_kids_topics(youtube_api_key, max_results=10)
    topic = topics[0]
    print(f"Topic: {topic}")

    print("Step 2: Generating script...")
    script = generate_kids_script(gemini_api_key, topic, language="English")
    title  = script.get("title", f"Fun {topic[:30]} Song")
    lyrics = script.get("lyrics", f"Let us learn about {topic[:30]} today, sing and dance and laugh and play!")
    tags   = [t.strip() for t in script.get("tags", "kids,educational,shorts,divijoytoons,rhymes").split(",")]
    print(f"Title: {title}")
    print(f"Lyrics: {lyrics[:80]}...")

    base = sanitize(title)

    print("Step 3: Translating lyrics to all languages...")
    texts_by_lang = translate_all_languages(lyrics)

    print("Step 4: Generating neural voices...")
    audio_files = generate_all_languages(texts_by_lang, base)

    print("Step 5: Creating videos...")
    youtube = get_youtube_service(credentials_file=credentials_file)

    LANG_LABELS = {
        "en": "English", "hi": "Hindi", "ta": "Tamil",
        "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"
    }
    for idx, (lang_code, audio_path) in enumerate(audio_files.items()):
        video_path = f"output/videos/{base}_{lang_code}.mp4"
        lang_lyrics = texts_by_lang.get(lang_code, lyrics)
        create_short_video(title, lang_lyrics, audio_path, video_path, color_index=idx)

        lang_label = LANG_LABELS.get(lang_code, lang_code.upper())
        print(f"Step 6: Uploading {lang_label} video...")
        upload_short(
            youtube=youtube,
            video_path=video_path,
            title=f"{title} | {lang_label}",
            description=f"DiviJoyToons | Kids Educational Short | {lang_label}\n\n#DiviJoyToons #KidsRhymes #Shorts",
            tags=tags + [lang_label],
            made_for_kids=True,
        )

    print("\nPipeline complete! All videos uploaded.")

if __name__ == "__main__":
    run()
