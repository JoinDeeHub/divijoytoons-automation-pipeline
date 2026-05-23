from moviepy import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, ImageClip
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import subprocess

BG_THEMES = [
    {"bg": (255, 240, 130), "accent": (255, 100, 80), "text": "#333333"},
    {"bg": (150, 220, 255), "accent": (30, 120, 255),  "text": "#111111"},
    {"bg": (255, 200, 210), "accent": (220, 60, 120),  "text": "#222222"},
    {"bg": (180, 255, 200), "accent": (30, 160, 80),   "text": "#111111"},
    {"bg": (230, 200, 255), "accent": (120, 50, 200),  "text": "#222222"},
    {"bg": (255, 220, 160), "accent": (200, 100, 20),  "text": "#222222"},
]

def get_available_font():
    candidates = [
        "DejaVuSans-Bold", "DejaVuSans", "FreeSansBold",
        "FreeSans", "LiberationSans-Bold", "LiberationSans",
    ]
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
    """Create a colorful gradient-style background with decorative circles."""
    img = Image.new("RGB", (width, height), theme["bg"])
    draw = ImageDraw.Draw(img)
    # Decorative circles for a fun kids look
    circles = [
        (100, 100, 180, theme["accent"]),
        (900, 200, 120, theme["accent"]),
        (200, 1700, 200, theme["accent"]),
        (850, 1800, 150, theme["accent"]),
        (540, 960, 300, tuple(min(255, c + 60) for c in theme["bg"])),
    ]
    for cx, cy, r, color in circles:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=color + (60,) if len(color) == 3 else color)
    # Stars
    for pos in [(80, 400), (950, 600), (100, 1200), (950, 1400)]:
        x, y = pos
        draw.polygon([
            (x, y - 30), (x + 10, y - 10), (x + 30, y),
            (x + 10, y + 10), (x, y + 30), (x - 10, y + 10),
            (x - 30, y), (x - 10, y - 10)
        ], fill=theme["accent"])
    arr = np.array(img)
    return ColorClip(arr, duration=duration)

def make_text_clip(text, font_size, color, font, duration, size, position):
    kwargs = dict(text=text, font_size=font_size, color=color,
                  method="caption", size=size)
    if font:
        kwargs["font"] = font
    return TextClip(**kwargs).with_position(position).with_duration(duration)

def create_short_video(title, lyrics, audio_path, output_path, color_index=0):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    theme = BG_THEMES[color_index % len(BG_THEMES)]
    duration = 20
    font = get_available_font()
    print(f"Using font: {font or 'default'}, Theme: {color_index}")

    bg = make_colorful_background(1080, 1920, theme, duration)

    # Top banner
    banner = ColorClip(size=(1080, 160), color=theme["accent"], duration=duration)\
        .with_position((0, 0))

    title_clip = make_text_clip(
        f"DiviJoyToons", 55, "white", font, duration, (1000, None), ("center", 40)
    )
    song_title = make_text_clip(
        title[:45], 68, theme["accent"], font, duration, (980, None), ("center", 220)
    )
    lyric_clip = make_text_clip(
        lyrics[:180], 54, theme["text"], font, duration, (900, None), ("center", 800)
    )
    # Bottom branding bar
    bottom = ColorClip(size=(1080, 120), color=theme["accent"], duration=duration)\
        .with_position((0, 1800))
    watermark = make_text_clip(
        "@DiviJoyToons | Kids Rhymes", 40, "white", font, duration, (900, None), ("center", 1830)
    )

    video = CompositeVideoClip(
        [bg, banner, title_clip, song_title, lyric_clip, bottom, watermark],
        size=(1080, 1920)
    )
    audio = AudioFileClip(audio_path)
    audio = audio.subclipped(0, min(duration, audio.duration))
    final = video.with_audio(audio)
    final.write_videofile(
        str(output_path), fps=24, codec="libx264",
        audio_codec="aac", logger=None
    )
    print(f"Video saved: {output_path}")
    return str(output_path)
