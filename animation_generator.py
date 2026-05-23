"""Generates animated cartoon clips using Kling AI image2video API."""
import os
import time
import jwt
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

KLING_ACCESS_KEY = os.getenv("KLING_ACCESS_KEY", "")
KLING_SECRET_KEY = os.getenv("KLING_SECRET_KEY", "")
KLING_API_BASE   = "https://api.klingai.com"

SCENE_PROMPTS = [
    "A cute animated cartoon baby girl dancing happily, colorful background, kids animation style, bright colors, 2D cartoon",
    "Colorful animated shapes bouncing and spinning, kids educational cartoon, cheerful music notes floating",
    "Animated cartoon stars and flowers growing, soft pastel colors, kids friendly, happy expression",
    "Cute cartoon animals waving and jumping, bright colorful meadow, kids 2D animation style",
]

def generate_jwt_token():
    payload = {
        "iss": KLING_ACCESS_KEY,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5,
    }
    return jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256")

def create_text2video(prompt, duration=5, aspect_ratio="9:16"):
    token = generate_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "model_name": "kling-v1",
        "prompt": prompt,
        "negative_prompt": "realistic, scary, dark, violence, adult content",
        "cfg_scale": 0.5,
        "mode": "std",
        "aspect_ratio": aspect_ratio,
        "duration": str(duration),
    }
    resp = requests.post(f"{KLING_API_BASE}/v1/videos/text2video",
                         headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    task_id = resp.json()["data"]["task_id"]
    print(f"  Task submitted: {task_id}")
    return task_id

def create_image2video(image_path, prompt, duration=5):
    import base64
    token = generate_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    body = {
        "model_name": "kling-v1",
        "image": image_b64,
        "prompt": prompt,
        "negative_prompt": "scary, dark, violence, realistic, adult",
        "duration": str(duration),
        "mode": "std",
        "cfg_scale": 0.5,
    }
    resp = requests.post(f"{KLING_API_BASE}/v1/videos/image2video",
                         headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    task_id = resp.json()["data"]["task_id"]
    print(f"  Image2video task: {task_id}")
    return task_id

def poll_task(task_id, endpoint="text2video", max_wait=300):
    waited = 0
    while waited < max_wait:
        token = generate_jwt_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{KLING_API_BASE}/v1/videos/{endpoint}/{task_id}"
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        status = result["data"]["task_status"]
        print(f"  Status: {status} ({waited}s)")
        if status == "succeed":
            return result["data"]["task_result"]["videos"][0]["url"]
        elif status == "failed":
            raise RuntimeError(f"Kling task failed: {result}")
        time.sleep(15)
        waited += 15
    raise TimeoutError(f"Kling task timed out after {max_wait}s")

def download_video(url, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  Clip downloaded: {output_path}")
    return output_path

def check_kling_credits():
    """Returns True if Kling account has credits available."""
    if not KLING_ACCESS_KEY or not KLING_SECRET_KEY:
        return False
    try:
        token = generate_jwt_token()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{KLING_API_BASE}/v1/account/costs",
                            headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            remaining = data.get("resource_pack_subscribe_infos", [])
            if remaining:
                print(f"  Kling credits available: {remaining}")
                return True
        # Try a dummy small request to check if 429 comes back
        return resp.status_code != 429
    except Exception:
        return False

def generate_animated_clips(topic, character_image=None, num_scenes=4, output_dir="output/clips"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    clip_paths = []
    for i in range(min(num_scenes, len(SCENE_PROMPTS))):
        prompt = f"{SCENE_PROMPTS[i]} Topic: {topic}"
        print(f"  Scene {i+1}/{num_scenes}: {prompt[:60]}...")
        try:
            if i == 0 and character_image and Path(character_image).exists():
                task_id = create_image2video(
                    character_image,
                    f"Cute cartoon girl dancing and singing about {topic}, happy, colorful, kids animation"
                )
                video_url = poll_task(task_id, endpoint="image2video")
            else:
                task_id = create_text2video(prompt, duration=5, aspect_ratio="9:16")
                video_url = poll_task(task_id, endpoint="text2video")
            clip_path = f"{output_dir}/scene_{i+1}.mp4"
            download_video(video_url, clip_path)
            clip_paths.append(clip_path)
        except Exception as e:
            err = str(e)
            if "429" in err or "Too Many Requests" in err:
                print(f"  Kling quota/credits exhausted. Skipping animation.")
                break  # Stop trying, use fallback
            print(f"  Scene {i+1} failed: {e}")
    return clip_paths
