import asyncio
import edge_tts
from pathlib import Path

# Natural neural voices per language
LANGUAGE_VOICES = {
    "en": "en-US-AriaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
}

async def _generate(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_voice(text, lang_code, output_path):
    output_path = str(Path(output_path))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    voice = LANGUAGE_VOICES.get(lang_code, "en-US-AriaNeural")
    asyncio.run(_generate(text, voice, output_path))
    print(f"Voice saved [{lang_code}]: {output_path}")
    return output_path

def generate_all_languages(texts_by_lang, base_filename):
    """texts_by_lang: dict of {lang_code: text}"""
    audio_files = {}
    for lang_code, text in texts_by_lang.items():
        try:
            path = f"output/audio/{base_filename}_{lang_code}.mp3"
            generate_voice(text, lang_code, path)
            audio_files[lang_code] = path
        except Exception as e:
            print(f"Voice failed [{lang_code}]: {e}")
    return audio_files
