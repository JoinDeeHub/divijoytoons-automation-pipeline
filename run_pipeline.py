from dotenv import load_dotenv
import os
import re
from trend_finder import get_trending_kids_topics
from script_generator import generate_kids_script
from voice_generator import generate_all_languages
from translator import translate_all_languages
from video_creator import create_short_video
from animation_generator import generate_animated_clips
from uploader import get_youtube_service, upload_short

load_dotenv()

def sanitize(text):
    """Clean filename: ASCII only, spaces to underscore, max 25 chars."""
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text).strip()
    text = re.sub(r"\s+", "_", text)
    return text[:25]

CHARACTER_IMAGE = "assets/character.jpg"

LANG_LABELS = {
    "en": "English", "hi": "Hindi", "ta": "Tamil",
    "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"
}

def run():
    youtube_api_key  = os.getenv("YOUTUBE_API_KEY", "")
    gemini_api_key   = os.getenv("GEMINI_API_KEY", "")
    credentials_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "credentials.json")
    kling_access     = os.getenv("KLING_ACCESS_KEY", "")

    # Step 1: Topic
    print("Step 1: Finding topic...")
    topics = get_trending_kids_topics(youtube_api_key, max_results=10)
    topic  = topics[0]
    print(f"  Topic: {topic}")

    # Step 2: Script
    print("\nStep 2: Generating script...")
    script = generate_kids_script(gemini_api_key, topic, language="English")
    title  = script.get("title",  f"{topic} Song for Kids")
    lyrics = script.get("lyrics", f"{topic}! Let us sing and play, learning every day!")
    tags   = [t.strip() for t in script.get("tags", "kids,educational,shorts,divijoytoons,rhymes").split(",")]
    # Ensure title is clean ASCII
    title  = title.encode('ascii', 'ignore').decode('ascii').strip()
    base   = sanitize(topic)  # Use TOPIC not title for filename
    print(f"  Title:  {title}")
    print(f"  File base: {base}")
    print(f"  Lyrics: {lyrics[:80]}...")

    # Step 3: Animated clips
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
            print(f"  Generated {len(clip_paths)} animated clips")
        except Exception as e:
            print(f"  Kling failed: {e} — using colorful fallback")
    else:
        print("  No KLING_ACCESS_KEY — using colorful fallback")

    # Step 4: Translate
    print("\nStep 4: Translating lyrics...")
    texts_by_lang = translate_all_languages(lyrics)

    # Step 5: Voices
    print("\nStep 5: Generating neural voices...")
    audio_files = generate_all_languages(texts_by_lang, base)

    # Step 6 + 7: Videos + Upload
    print("\nStep 6: Creating videos and uploading...")
    youtube = get_youtube_service(credentials_file=credentials_file)

    for idx, (lang_code, audio_path) in enumerate(audio_files.items()):
        lang_label  = LANG_LABELS.get(lang_code, lang_code.upper())
        video_path  = f"output/videos/{base}_{lang_code}.mp4"
        lang_lyrics = texts_by_lang.get(lang_code, lyrics)

        print(f"\n  [{lang_label}] Creating video...")
        create_short_video(
            title, lang_lyrics, audio_path, video_path,
            color_index=idx, clip_paths=clip_paths
        )

        print(f"  [{lang_label}] Uploading...")
        upload_short(
            youtube=youtube,
            video_path=video_path,
            title=f"{title} | {lang_label}",
            description=(
                f"DiviJoyToons | {topic} | Kids Educational Short | {lang_label}\n"
                f"\nFun learning for children aged 1-6!"
                f"\n\n#DiviJoyToons #KidsRhymes #Shorts #{topic.replace(' ', '')}"
            ),
            tags=tags + [lang_label, topic],
            made_for_kids=True,
            lang_code=lang_code,
        )

    print("\nPipeline complete!")

if __name__ == "__main__":
    run()
