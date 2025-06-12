from script_model import Script
import json, os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy import ImageClip, concatenate_videoclips
from moviepy import TextClip, CompositeVideoClip, CompositeAudioClip
from moviepy.video.tools.subtitles import SubtitlesClip
import logging

# === LOGGER SETUP ===
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

def load_audio_clip(s: Script):
    audio_path=f"./{s.title}/audio.mp3"
    try:
        audio_clip = AudioFileClip(audio_path)
    except Exception as e:
        print(f"An error occurred while loading the audio: {e}")
        raise e
    return audio_clip

def generate_video_clip(s: Script, audio_clip: AudioFileClip):
    logging.info(f"🎬 Generating video for {s.title}...")
    image_files = sorted([f"{s.title}/{f}" for f in os.listdir(s.title) if f.endswith(".png")])
    num_images = len(image_files)
    bg_music = "background_music.mp3"
    music = AudioFileClip(bg_music).subclipped(21.5)  # skip first seconds
    music = music.with_volume_scaled(0.40)
    music = music.with_duration(audio_clip.duration+1) 

    final_audio = CompositeAudioClip([audio_clip, music])

    f1 = 3.576
    f2 = 7.232
    f3 = 11.192
    segment_duration = [f1, f2-f1 , f3-f2, final_audio.duration-f3]

    clips = []
    for img_path, duration in zip(image_files, segment_duration):
        clip = (
            ImageClip(img_path)
            .resized(lambda t: 1 + 0.05 * t)  # Apply zoom-in effect
            .with_duration(duration)
            .with_position("center")
        )
        clips.append(clip)

    video_clip = concatenate_videoclips(clips, method="compose").with_audio(final_audio)

    subtitles_clip = SubtitlesClip(f"{s.title}/subtitles.srt", make_textclip=subtitle_generator)

    subtitles_clip = subtitles_clip.with_position(("center", "center")) 

    # Combine with video
    final_video = CompositeVideoClip([video_clip, subtitles_clip])

    output_file = f"./{s.title}/{s.title}.mp4"
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=24)
    

def subtitle_generator(txt):
    return TextClip(
        font="DejaVuSans",
        text=txt,
        font_size=100,        
        color="white",
        stroke_color="black",
        stroke_width=5,
        method="caption",
        text_align="center",
        horizontal_align="center",
        size=(900, None),
        margin=(80,50),
        interline=6
    )
    

if __name__ == "__main__":
    input_path = "stoicism.json" 
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    for script in scripts[6:7]:
        s = Script(**script)
        logger.info(f"{s.title}")
        audio_clip = load_audio_clip(s)

        video_clip = generate_video_clip(s, audio_clip)