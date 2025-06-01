from script_model import Script
from text_to_speech import generate_audio
import json, os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.io.ffplay_audiopreviewer import ffplay_audiopreview
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

if __name__ == "__main__":
    input_path = "scripts.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[0])
    audio_path=f"{s.title}/audio.mp3"
    audio_clip = AudioFileClip(audio_path)
    #ffplay_audiopreview(audio)

    image_files = sorted([f"{s.title}/{f}" for f in os.listdir(s.title) if f.endswith(".png")])
    num_images = len(image_files)
    segment_duration = audio_clip.duration / num_images

    clips = []
    start_time = 0
    
    fps = num_images / audio_clip.duration
    video_clip = ImageSequenceClip(image_files, fps)
    final_clip = video_clip.with_audio(audio_clip)

    # === EXPORT FINAL VIDEO ===
    output_file = f"{s.title}/video.mp4"
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')