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

STANDARD_RESOLUTION = (1080, 1920)

def load_audio_clip(title: str):
    audio_path=f"./{title}/audio.mp3"
    try:
        audio_clip = AudioFileClip(audio_path)
    except Exception as e:
        print(f"An error occurred while loading the audio: {e}")
        raise e
    return audio_clip

def generate_video_clip(title: str):
    logging.info(f"🎬 Generating video for {title}...")
    image_files = sorted([f"{title}/{f}" for f in os.listdir(title) if f.endswith(".png")])
    num_images = len(image_files)

    audio_clip = load_audio_clip(title)
    bg_music = "background_music.mp3"
    music = AudioFileClip(bg_music).subclipped(21.5)  # skip first seconds
    music = music.with_volume_scaled(0.40)
    music = music.with_duration(audio_clip.duration+1) 

    final_audio = CompositeAudioClip([audio_clip, music])

    image_start = [0.0, 2.774, 7.535, 12.492, final_audio.duration]
    segment_duration = [image_start[i+1] - image_start[i] for i in range(len(image_start)-1)]

    clips = []
    for img_path, duration in zip(image_files, segment_duration):
        clip = (
            ImageClip(img_path)
            .resized(height=STANDARD_RESOLUTION[1])
            .resized(lambda t: 1 + 0.05 * t)  # Apply zoom-in effect
            .with_duration(duration)
            .with_position("center")
        )
        clips.append(clip)

    video_clip = concatenate_videoclips(clips, method="compose").with_audio(final_audio)

    subtitles_clip = SubtitlesClip(f"{title}/subtitles.srt", make_textclip=subtitle_generator)

    subtitles_clip = subtitles_clip.with_position(("center", "center")) 
    
    # Combine with video
    final_video = CompositeVideoClip([video_clip, subtitles_clip])

    output_file = f"./{title}/{title}.mp4"
    
    final_video.write_videofile(output_file,
                               codec='libx264',
                               audio_codec='aac', 
                               fps=30, bitrate="8M", 
                               preset="slow", 
                               threads=4)
    

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
    title = "Stoic Morning Routine"
    video_clip = generate_video_clip(title)