from script_model import Script
import json, os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy import ImageClip, concatenate_videoclips
from moviepy import TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

def load_audio_clip(s: Script):
    audio_path=f"./{s.title}/audio.mp3"
    try:
        audio_clip = AudioFileClip(audio_path)
    except Exception as e:
        print(f"An error occurred while loading the audio: {e}")
        raise e
    return audio_clip

def generate_video_clip(s: Script, audio_clip: AudioFileClip):
    image_files = sorted([f"{s.title}/{f}" for f in os.listdir(s.title) if f.endswith(".png")])
    num_images = len(image_files)
    segment_duration = audio_clip.duration / num_images

    clips = []
    for img_path in image_files:
        clip = (
            ImageClip(img_path)
            .resized(lambda t: 1 + 0.02 * t)  # Apply zoom-in effect
            .with_duration(segment_duration)
            .with_position("center")
        )
        clips.append(clip)

    return concatenate_videoclips(clips, method="compose").with_audio(audio_clip)

def subtitle_generator(txt):
    return TextClip(
        font="DejaVuSans",
        text=txt,
        font_size=60,        
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
    input_path = "scripts.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    for script in scripts[:1]:
        s = Script(**script)
        audio_clip = load_audio_clip(s)

        video_clip = generate_video_clip(s, audio_clip)

        subtitles_clip = SubtitlesClip(f"{s.title}/subtitles.srt", make_textclip=subtitle_generator)

        # Set position at runtime using a lambda (this works!)
        subtitles_clip = subtitles_clip.with_position(("center", "center")) 

        # Combine with video
        final_video = CompositeVideoClip([video_clip, subtitles_clip])


        # === EXPORT FINAL VIDEO ===
        output_file = f"./{s.title}/video.mp4"
        final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=24)