import requests

def get_trending_kids_topics(api_key, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "type": "video",
        "videoDuration": "short",
        "safeSearch": "strict",
        "videoCategoryId": "27",
        "order": "viewCount",
        "maxResults": max_results,
        "q": "kids educational animated shorts",
        "key": api_key,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [i["snippet"]["title"] for i in items]
