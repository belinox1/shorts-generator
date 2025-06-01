import os
import json
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from script_model import Script

load_dotenv()
elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def generate_subtitles_from_alignment(alignment: dict, filename: str):
    characters = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    srt_lines = []
    index = 1
    word = ""
    start_time = None

    for c, start, end in zip(characters, starts, ends):
        if c != " ":
            if word == "":
                start_time = start
            word += c
            end_time = end
        elif word:
            srt_lines.append(f"{index}\n{format_time(start_time)} --> {format_time(end_time)}\n{word}\n")
            index += 1
            word = ""

    if word:
        srt_lines.append(f"{index}\n{format_time(start_time)} --> {format_time(end_time)}\n{word}\n")

    srt_text = "\n".join(srt_lines)
    with open(filename, "w", encoding="utf-8") as f:
          f.write(srt_text)

def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def generate_audio(text: str, filename: str):
    audio = elevenlabs.text_to_speech.convert_with_timestamps(
        text=text,
        voice_id="nPczCjzI2devNBz1zQrb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    save(audio.audio_base_64au, filename)
    return audio

# === ENTRY POINT ===
if __name__ == "__main__":
    input_path = "scripts.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[0])

    output_dir = s.title
    os.makedirs(output_dir, exist_ok=True)
    audio_filename = os.path.join(output_dir, f"audio.mp3")
    subtitle_filename = os.path.join(output_dir, f"subtitles.srt")
    audio = generate_audio(s.text, audio_filename)
    srt = generate_subtitles_from_alignment(audio.alignment, subtitle_filename)