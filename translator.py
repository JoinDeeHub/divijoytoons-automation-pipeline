from deep_translator import GoogleTranslator

LANG_MAP = {
    "en": "english",
    "hi": "hindi",
    "ta": "tamil",
    "te": "telugu",
    "kn": "kannada",
    "ml": "malayalam",
}

def translate_lyrics(text, lang_code):
    if lang_code == "en":
        return text
    try:
        translated = GoogleTranslator(
            source="english",
            target=LANG_MAP.get(lang_code, "english")
        ).translate(text)
        print(f"Translated to {lang_code}: {translated[:60]}...")
        return translated
    except Exception as e:
        print(f"Translation failed for {lang_code}: {e}")
        return text

def translate_all_languages(text):
    return {lang: translate_lyrics(text, lang) for lang in LANG_MAP}
