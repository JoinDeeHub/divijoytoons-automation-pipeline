import google.generativeai as genai

def generate_kids_script(gemini_api_key, topic, language="English"):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""Create a 20-30 second kids educational nursery rhyme for YouTube Shorts.
Topic: {topic}
Language: {language}
Safe for ages 1-6, simple, repetitive, catchy, and educational.

Return in this exact format:
TITLE: [catchy title]
LYRICS: [rhyme lyrics]
SCENE: [simple animation description]
TAGS: [5 comma separated tags]"""
    response = model.generate_content(prompt)
    text = response.text
    result = {}
    for line in text.split("\n"):
        for key in ["TITLE", "LYRICS", "SCENE", "TAGS"]:
            if line.startswith(f"{key}:"):
                result[key.lower()] = line.replace(f"{key}:", "").strip()
    return result
