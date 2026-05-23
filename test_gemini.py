from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

models_to_test = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
]

for model in models_to_test:
    try:
        r = client.models.generate_content(model=model, contents="Say hello")
        print(f"[OK] {model}: {r.text[:50]}")
        break
    except Exception as e:
        print(f"[FAIL] {model}: {str(e)[:80]}")
