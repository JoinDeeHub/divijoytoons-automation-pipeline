from moviepy import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from pathlib import Path
import subprocess

BG_COLORS = [
    (255, 230, 120),
    (180, 230, 255),
    (255, 200, 200),
    (200, 255, 210),
]

def get_available_font():
    """Auto-detect a usable font from the system."""
    candidates = [
        "DejaVuSans-Bold",
        "DejaVuSans",
        "FreeSansBold",
        "FreeSans",
        "LiberationSans-Bold",
        "LiberationSans",
        "Arial",
        "Helvetica",
    ]
    try:
        result = subprocess.run(
            ["fc-list", "--format=%{file}\n"],
            capture_output=True, text=True
        )
        available = result.stdout.lower()
        for font in candidates:
            if font.lower().replace("-", "") in available.replace("-", "").replace(" ", ""):
                return font
    except Exception:
        pass
    # Last resort: return None to use moviepy default
    return None

def make_text_clip(text, font_size, color, font, duration, size, position):
    kwargs = dict(
        text=text,
        font_size=font_size,
        color=color,
        method="caption",
        size=size,
    )
    if font:
        kwargs["font"] = font
    return (
        TextClip(**kwargs)
        .with_position(position)
        .with_duration(duration)
    )

def create_short_video(title, lyrics, audio_path, output_path, color_index=0):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bg_color = BG_COLORS[color_index % len(BG_COLORS)]
    duration = 20
    font = get_available_font()
    print(f"Using font: {font or 'moviepy default'}")

    bg = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
    title_clip = make_text_clip(
        title[:50], 70, "white", font, duration, (1000, None), ("center", 150)
    )
    lyric_clip = make_text_clip(
        lyrics[:200], 52, "#222222", font, duration, (900, None), ("center", 700)
    )
    watermark = make_text_clip(
        "DiviJoyToons", 38, "white", font, duration, (600, None), ("center", 1820)
    )
    video = CompositeVideoClip([bg, title_clip, lyric_clip, watermark], size=(1080, 1920))
    audio = AudioFileClip(audio_path)
    audio = audio.subclipped(0, min(duration, audio.duration))
    final = video.with_audio(audio)
    final.write_videofile(
        str(output_path), fps=24, codec="libx264",
        audio_codec="aac", logger=None
    )
    print(f"Video saved: {output_path}")
    return str(output_path)
