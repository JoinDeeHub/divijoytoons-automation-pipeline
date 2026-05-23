import requests
import re
import random

# High quality original safe topics — no garbage from YouTube titles
ORIGINAL_TOPICS = [
    "Counting 1 to 10",
    "Colors of the Rainbow",
    "Farm Animals",
    "Good Morning Song",
    "Alphabet A to Z",
    "Shapes Circle Square Triangle",
    "Days of the Week",
    "Fruits and Vegetables",
    "Body Parts Song",
    "Weather Sunny Rainy Cloudy",
    "Baby Animals",
    "Bedtime Lullaby",
    "Please and Thank You",
    "Wash Your Hands",
    "Brush Your Teeth",
    "Numbers Song",
    "Seasons Spring Summer Autumn Winter",
    "Under the Sea",
    "Happy Birthday Song",
    "Good Night Song",
]

COPYRIGHTED_BRANDS = [
    "cocomelon", "chuchu", "pinkfong", "blippi", "peppa",
    "nursery rhymes tv", "little baby bum", "super simple",
    "baby shark", "bounce patrol", "dave and ava",
    "min tot", "tot", "hindi rhye", "rhye",
]

def is_clean_english(text):
    """Check if text is clean ASCII English only."""
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def is_safe_topic(title):
    title_lower = title.lower()
    for brand in COPYRIGHTED_BRANDS:
        if brand in title_lower:
            return False
    if not is_clean_english(title):
        return False
    if len(title.strip()) < 5:
        return False
    return True

def extract_clean_topic(title):
    title = re.sub(r"@\w+", "", title)
    title = re.sub(r"#\w+", "", title)
    title = re.sub(r"[|\-&amp;]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    # Only keep if result is clean and meaningful
    words = title.split()
    if len(words) < 2:
        return None
    return " ".join(words[:6])  # Max 6 words

def get_trending_kids_topics(api_key, max_results=10):
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "type": "video",
            "videoDuration": "short",
            "safeSearch": "strict",
            "videoCategoryId": "27",
            "order": "viewCount",
            "maxResults": max_results,
            "q": "kids educational animated song counting alphabet",
            "key": api_key,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        items = r.json().get("items", [])
        safe_topics = []
        for item in items:
            title = item["snippet"]["title"]
            if is_safe_topic(title):
                clean = extract_clean_topic(title)
                if clean and is_safe_topic(clean):
                    safe_topics.append(clean)
        if safe_topics:
            print(f"Found {len(safe_topics)} safe trending topics")
            return safe_topics
    except Exception as e:
        print(f"Trend fetch failed: {e}")

    # Always use original curated topics as fallback
    print("Using original safe topic list")
    random.shuffle(ORIGINAL_TOPICS)
    return ORIGINAL_TOPICS[:5]
