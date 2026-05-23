from moviepy import ImageClip, TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import subprocess

BG_THEMES = [
    {"bg": (255, 240, 130), "accent": (220, 80, 50),  "text": "#222222"},
    {"bg": (150, 220, 255), "accent": (20, 100, 220), "text": "#111111"},
    {"bg": (255, 200, 210), "accent": (200, 50, 110), "text": "#222222"},
    {"bg": (180, 255, 200), "accent": (20, 140, 70),  "text": "#111111"},
    {"bg": (230, 200, 255), "accent": (110, 40, 190), "text": "#222222"},
    {"bg": (255, 220, 160), "accent": (190, 90, 10),  "text": "#222222"},
]

def get_available_font():
    candidates = ["DejaVuSans-Bold", "DejaVuSans", "FreeSansBold",
                  "FreeSans", "LiberationSans-Bold", "LiberationSans"]
    try:
        result = subprocess.run(["fc-list", "--format=%{file}\n"],
                                capture_output=True, text=True)
        available = result.stdout.lower()
        for font in candidates:
            if font.lower().replace("-", "") in available.replace("-", "").replace(" ", ""):
                return font
    except Exception:
        pass
    return None

def make_colorful_background(width, height, theme, duration):
    img = Image.new("RGB", (width, height), theme["bg"])
    draw = ImageDraw.Draw(img)
    for cx, cy, r in [(100,150,160),(950,250,120),(200,1700,180),(880,1780,150),(540,960,260)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=theme["accent"])
    for x, y in [(80,450),(950,650),(100,1250),(950,1450)]:
        pts = [(x,y-28),(x+9,y-9),(x+28,y),(x+9,y+9),(x,y+28),(x-9,y+9),(x-28,y),(x-9,y-9)]
        draw.polygon(pts, fill=theme["accent"])
    return ImageClip(np.array(img), duration=duration)

def make_banner(width, height, color, duration, y_pos):
    img = Image.new("RGB", (width, height), color)
    return ImageClip(np.array(img), duration=duration).with_position((0, y_pos))

def make_text_clip(text, font_size, color, font, duration, size, position):
    kwargs = dict(text=text, font_size=font_size, color=color, method="caption", size=size)
    if font:
        kwargs["font"] = font
    return TextClip(**kwargs).with_position(position).with_duration(duration)

def create_short_video(title, lyrics, audio_path, output_path, color_index=0, clip_paths=None):
    """Create a Short video. Uses animated clips if available, else colorful fallback."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    theme    = BG_THEMES[color_index % len(BG_THEMES)]
    duration = 20
    font     = get_available_font()
    print(f"Using font: {font or 'default'}, Theme: {color_index}")

    # --- Background: animated clips or colorful fallback ---
    if clip_paths and len(clip_paths) > 0:
        print(f"  Using {len(clip_paths)} animated Kling clips as background")
        clips = [VideoFileClip(p).resized((1080, 1920)) for p in clip_paths if Path(p).exists()]
        if clips:
            bg = concatenate_videoclips(clips, method="compose").with_duration(duration)
        else:
            bg = make_colorful_background(1080, 1920, theme, duration)
    else:
        bg = make_colorful_background(1080, 1920, theme, duration)

    top_bar    = make_banner(1080, 170, theme["accent"], duration, 0)
    bot_bar    = make_banner(1080, 120, theme["accent"], duration, 1800)
    brand      = make_text_clip("DiviJoyToons", 58, "white", font, duration, (1000, None), ("center", 45))
    song_title = make_text_clip(title[:45], 66, theme["accent"], font, duration, (980, None), ("center", 230))
    lyric_clip = make_text_clip(lyrics[:200], 52, theme["text"], font, duration, (900, None), ("center", 820))
    watermark  = make_text_clip("@DiviJoyToons | Kids Rhymes", 38, "white", font, duration, (900, None), ("center", 1832))

    video = CompositeVideoClip([bg, top_bar, brand, song_title, lyric_clip, bot_bar, watermark], size=(1080, 1920))
    audio = AudioFileClip(audio_path)
    audio = audio.subclipped(0, min(duration, audio.duration))
    final = video.with_audio(audio)
    final.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", logger=None)
    print(f"Video saved: {output_path}")
    return str(output_path)
