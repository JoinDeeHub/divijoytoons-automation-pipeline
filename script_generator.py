from google import genai
import time

def generate_kids_script(gemini_api_key, topic, language="English", retries=3):
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

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            text = response.text
            result = {}
            for line in text.split("\n"):
                for key in ["TITLE", "LYRICS", "SCENE", "TAGS"]:
                    if line.startswith(f"{key}:"):
                        result[key.lower()] = line.replace(f"{key}:", "").strip()
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                wait = 30 * (attempt + 1)
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)
    print("Script generation failed after retries. Using fallback script.")
    return {
        "title": f"Fun {topic} Song",
        "lyrics": f"Let us learn about {topic} today, sing and dance and laugh and play!",
        "scene": "Colorful animated characters dancing",
        "tags": "kids,educational,shorts,divijoytoons,rhymes",
    }
