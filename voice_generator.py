from gtts import gTTS
from pathlib import Path

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
}

def generate_voice(text, lang_code, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(str(output_path))
    print(f"Voice saved: {output_path}")
    return str(output_path)

def generate_all_languages(text, base_filename):
    audio_files = {}
    for lang_name, lang_code in LANGUAGE_CODES.items():
        try:
            path = generate_voice(text, lang_code, f"output/audio/{base_filename}_{lang_code}.mp3")
            audio_files[lang_code] = path
        except Exception as e:
            print(f"{lang_name} voice failed: {e}")
    return audio_files
