from google import genai
from google.genai import types

def generate_kids_script(gemini_api_key, topic, language="English"):
    client = genai.Client(api_key=gemini_api_key)
    prompt = f"""Create a 20-30 second kids educational nursery rhyme for YouTube Shorts.
Topic: {topic}
Language: {language}
Safe for ages 1-6, simple, repetitive, catchy, and educational.

Return in this exact format:
TITLE: [catchy title]
LYRICS: [rhyme lyrics]
SCENE: [simple animation description]
TAGS: [5 comma separated tags]"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    text = response.text
    result = {}
    for line in text.split("\n"):
        for key in ["TITLE", "LYRICS", "SCENE", "TAGS"]:
            if line.startswith(f"{key}:"):
                result[key.lower()] = line.replace(f"{key}:", "").strip()
    return result
