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

# Scene prompts for each topic — kids cartoon style
SCENE_PROMPTS = [
    "A cute animated cartoon baby girl dancing happily, colorful background, kids animation style, bright colors, 2D cartoon",
    "Colorful animated shapes bouncing and spinning, kids educational cartoon, cheerful music notes floating",
    "Animated cartoon stars and flowers growing, soft pastel colors, kids friendly, happy expression",
    "Cute cartoon animals waving and jumping, bright colorful meadow, kids 2D animation style",
]

def generate_jwt_token():
    """Generate JWT token for Kling API authentication."""
    payload = {
        "iss": KLING_ACCESS_KEY,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5,
    }
    return jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256")

def create_text2video(prompt, duration=5, aspect_ratio="9:16"):
    """Submit a text-to-video generation job to Kling AI."""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "model_name": "kling-v1",
        "prompt": prompt,
        "negative_prompt": "realistic, scary, dark, violence, adult content",
        "cfg_scale": 0.5,
        "mode": "std",
        "aspect_ratio": aspect_ratio,
        "duration": str(duration),
    }
    resp = requests.post(
        f"{KLING_API_BASE}/v1/videos/text2video",
        headers=headers, json=body, timeout=60
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = data["data"]["task_id"]
    print(f"  Task submitted: {task_id}")
    return task_id

def create_image2video(image_path, prompt, duration=5):
    """Animate a cartoon character image using Kling image2video."""
    token = generate_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    with open(image_path, "rb") as f:
        files = {"image": (Path(image_path).name, f, "image/jpeg")}
        data  = {
            "model_name": "kling-v1",
            "prompt": prompt,
            "negative_prompt": "scary, dark, violence, realistic, adult",
            "duration": str(duration),
            "mode": "std",
            "cfg_scale": "0.5",
        }
        resp = requests.post(
            f"{KLING_API_BASE}/v1/videos/image2video",
            headers=headers, files=files, data=data, timeout=60
        )
    resp.raise_for_status()
    task_id = resp.json()["data"]["task_id"]
    print(f"  Image2video task submitted: {task_id}")
    return task_id

def poll_task(task_id, endpoint="text2video", max_wait=300):
    """Poll Kling task until complete, return video URL."""
    token = generate_jwt_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{KLING_API_BASE}/v1/videos/{endpoint}/{task_id}"
    waited = 0
    while waited < max_wait:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        status = result["data"]["task_status"]
        print(f"  Status: {status} ({waited}s)")
        if status == "succeed":
            video_url = result["data"]["task_result"]["videos"][0]["url"]
            return video_url
        elif status == "failed":
            raise RuntimeError(f"Kling task failed: {result}")
        time.sleep(15)
        waited += 15
        token = generate_jwt_token()
        headers = {"Authorization": f"Bearer {token}"}
    raise TimeoutError(f"Kling task timed out after {max_wait}s")

def download_video(url, output_path):
    """Download generated video clip."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  Clip downloaded: {output_path}")
    return output_path

def generate_animated_clips(topic, character_image=None, num_scenes=4, output_dir="output/clips"):
    """Generate multiple animated cartoon clips for a topic."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    clip_paths = []

    for i in range(min(num_scenes, len(SCENE_PROMPTS))):
        prompt = f"{SCENE_PROMPTS[i]} Topic: {topic}"
        print(f"\nGenerating scene {i+1}/{num_scenes}: {prompt[:60]}...")
        try:
            if i == 0 and character_image and Path(character_image).exists():
                # Animate the DiviJoyToons character for scene 1
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
            print(f"  Scene {i+1} failed: {e}")
    return clip_paths

if __name__ == "__main__":
    clips = generate_animated_clips(
        topic="Shapes Circle Square Triangle",
        character_image="assets/character.jpg",
        num_scenes=4
    )
    print(f"\nGenerated {len(clips)} animated clips: {clips}")
