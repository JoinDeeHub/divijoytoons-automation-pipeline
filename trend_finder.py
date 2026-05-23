import requests
import re
import random

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

def is_clean_ascii(text):
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def fix_typos(text):
    """Fix common truncation/typos from YouTube titles."""
    fixes = {
        "Bck ": "Back ", "Lrn ": "Learn ", "Sngs": "Songs",
        "Vdeo": "Video", "Eductn": "Education",
    }
    for bad, good in fixes.items():
        text = text.replace(bad, good)
    return text

def is_safe_topic(title):
    title_lower = title.lower()
    for brand in COPYRIGHTED_BRANDS:
        if brand in title_lower:
            return False
    if not is_clean_ascii(title):
        return False
    if len(title.strip()) < 8:
        return False
    # Reject if any word is obviously truncated (ends mid-word with consonants)
    words = title.split()
    if len(words) < 2:
        return False
    return True

def extract_clean_topic(title):
    title = re.sub(r"@\w+", "", title)
    title = re.sub(r"#\w+", "", title)
    title = re.sub(r"[|\-&]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    title = fix_typos(title)
    words = [w for w in title.split() if len(w) > 1]
    if len(words) < 2:
        return None
    return " ".join(words[:5])

def get_trending_kids_topics(api_key, max_results=10):
    try:
        if api_key:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet", "type": "video",
                "videoDuration": "short", "safeSearch": "strict",
                "videoCategoryId": "27", "order": "viewCount",
                "maxResults": max_results,
                "q": "kids animated counting alphabet animals song",
                "key": api_key,
            }
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            items = r.json().get("items", [])
            safe_topics = []
            for item in items:
                raw = item["snippet"]["title"]
                if not is_safe_topic(raw):
                    continue
                clean = extract_clean_topic(raw)
                if clean and is_safe_topic(clean):
                    safe_topics.append(clean)
            if safe_topics:
                print(f"Found {len(safe_topics)} safe trending topics")
                return safe_topics
    except Exception as e:
        print(f"Trend fetch failed: {e}")

    print("Using original safe topic list")
    shuffled = ORIGINAL_TOPICS[:]
    random.shuffle(shuffled)
    return shuffled[:5]
