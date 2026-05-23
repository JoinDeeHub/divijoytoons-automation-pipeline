from dotenv import load_dotenv
import os
from trend_finder import get_trending_kids_topics
from script_generator import generate_kids_script
from voice_generator import generate_all_languages
from translator import translate_all_languages
from video_creator import create_short_video
from animation_generator import generate_animated_clips
from uploader import get_youtube_service, upload_short
import re

load_dotenv()

def sanitize(text):
    return re.sub(r"[^a-zA-Z0-9_]", "_", text)[:30]

CHARACTER_IMAGE = "assets/character.jpg"

def run():
    youtube_api_key  = os.getenv("YOUTUBE_API_KEY", "")
    gemini_api_key   = os.getenv("GEMINI_API_KEY", "")
    credentials_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "credentials.json")
    kling_access     = os.getenv("KLING_ACCESS_KEY", "")

    print("Step 1: Finding trending topic...")
    topics = get_trending_kids_topics(youtube_api_key, max_results=10)
    topic  = topics[0]
    print(f"Topic: {topic}")

    print("\nStep 2: Generating script...")
    script = generate_kids_script(gemini_api_key, topic, language="English")
    title  = script.get("title",  f"Fun {topic[:30]} Song")
    lyrics = script.get("lyrics", f"Let us learn about {topic[:30]} today, sing and dance and laugh and play!")
    tags   = [t.strip() for t in script.get("tags", "kids,educational,shorts,divijoytoons,rhymes").split(",")]
    print(f"Title:  {title}")
    print(f"Lyrics: {lyrics[:80]}...")

    base = sanitize(title)

    print("\nStep 3: Generating animated Kling clips...")
    clip_paths = []
    if kling_access:
        try:
            clip_paths = generate_animated_clips(
                topic=topic,
                character_image=CHARACTER_IMAGE,
                num_scenes=4,
                output_dir=f"output/clips/{base}"
            )
            print(f"Generated {len(clip_paths)} animated clips")
        except Exception as e:
            print(f"Kling animation failed: {e} — using fallback background")
    else:
        print("No KLING_ACCESS_KEY set — using fallback colorful background")

    print("\nStep 4: Translating lyrics...")
    texts_by_lang = translate_all_languages(lyrics)

    print("\nStep 5: Generating neural voices...")
    audio_files = generate_all_languages(texts_by_lang, base)

    print("\nStep 6: Creating videos...")
    youtube = get_youtube_service(credentials_file=credentials_file)

    LANG_LABELS = {
        "en": "English", "hi": "Hindi", "ta": "Tamil",
        "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"
    }
    for idx, (lang_code, audio_path) in enumerate(audio_files.items()):
        video_path  = f"output/videos/{base}_{lang_code}.mp4"
        lang_lyrics = texts_by_lang.get(lang_code, lyrics)
        lang_label  = LANG_LABELS.get(lang_code, lang_code.upper())
        create_short_video(
            title, lang_lyrics, audio_path, video_path,
            color_index=idx, clip_paths=clip_paths
        )
        print(f"\nStep 7: Uploading {lang_label}...")
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
