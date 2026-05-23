from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from pathlib import Path

BG_COLORS = [
    (255, 230, 120),
    (180, 230, 255),
    (255, 200, 200),
    (200, 255, 210),
]

def create_short_video(title, lyrics, audio_path, output_path, color_index=0):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bg_color = BG_COLORS[color_index % len(BG_COLORS)]
    duration = 20
    bg = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
    title_clip = (
        TextClip(title, fontsize=70, color="white", font="DejaVu-Sans-Bold",
                 method="caption", size=(1000, None))
        .set_position(("center", 150))
        .set_duration(duration)
    )
    lyric_clip = (
        TextClip(lyrics, fontsize=52, color="#222222", font="DejaVu-Sans",
                 method="caption", size=(900, None))
        .set_position(("center", 700))
        .set_duration(duration)
    )
    watermark = (
        TextClip("DiviJoyToons", fontsize=38, color="white", font="DejaVu-Sans-Bold")
        .set_position(("center", 1820))
        .set_duration(duration)
    )
    video = CompositeVideoClip([bg, title_clip, lyric_clip, watermark], size=(1080, 1920))
    audio = AudioFileClip(audio_path)
    audio = audio.subclip(0, min(duration, audio.duration))
    final = video.set_audio(audio)
    final.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac",
                          verbose=False, logger=None)
    print(f"Video saved: {output_path}")
    return str(output_path)
