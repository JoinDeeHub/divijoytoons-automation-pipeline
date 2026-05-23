import requests
import re

# Safe original educational topics for kids
# These are used when API topics are unsafe or copyrighted
FALLBACK_TOPICS = [
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
]

# Channel names/brands to avoid copying
COPYRIGHTED_BRANDS = [
    "cocomelon", "chuchu", "pinkfong", "blippi", "peppa",
    "nursery rhymes tv", "little baby bum", "super simple",
    "baby shark", "bounce patrol", "dave and ava",
]

def is_safe_topic(title):
    """Check if a trending title is safe to use as topic inspiration."""
    title_lower = title.lower()
    for brand in COPYRIGHTED_BRANDS:
        if brand in title_lower:
            return False
    return True

def extract_clean_topic(title):
    """Extract a clean educational topic from a video title."""
    # Remove channel names, special chars, hashtags
    title = re.sub(r"@\w+", "", title)
    title = re.sub(r"#\w+", "", title)
    title = re.sub(r"[|\-\|&amp;]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    # Take first 40 chars as topic
    return title[:40].strip()

def get_trending_kids_topics(api_key, max_results=10):
    """Fetch trending educational kids topics, filtered for safety."""
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
            "q": "kids educational song animated",
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
                if clean:
                    safe_topics.append(clean)
        if safe_topics:
            print(f"Found {len(safe_topics)} safe trending topics")
            return safe_topics
    except Exception as e:
        print(f"Trend fetch failed: {e}")

    # Always fall back to original safe topics
    import random
    print("Using original safe topic list")
    return [random.choice(FALLBACK_TOPICS)]
