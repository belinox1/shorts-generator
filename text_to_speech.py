import os
import json
import base64
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import CharacterAlignmentResponseModel
from script_model import Script

load_dotenv()
elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def split_text_into_lines(text, max_chars=40):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Ensure only two lines per subtitle
    if len(lines) > 2:
        mid = len(words) // 2
        return [
            " ".join(words[:mid]),
            " ".join(words[mid:])
        ]
    return lines

def generate_subtitles_from_alignment(alignment, filename: str, max_chars_per_line=40):
    characters = alignment.characters
    starts = alignment.character_start_times_seconds
    ends = alignment.character_end_times_seconds

    srt_lines = []
    index = 1
    word = ""
    word_start = None
    word_buffer = []

    for i, (char, start, end) in enumerate(zip(characters, starts, ends)):
        if char != " ":
            if not word:
                word_start = start
            word += char
        if char == " " or i == len(characters) - 1:
            if word:
                word_end = end
                word_buffer.append((word, word_start, word_end))
                word = ""

        line_duration = word_buffer[-1][2] - word_buffer[0][1] if word_buffer else 0
        if (
            len(word_buffer) >= 5 or
            (word_buffer and word_buffer[-1][0][-1] in ".?!") or
            line_duration > 2.5
        ):
            text = " ".join(w for w, _, _ in word_buffer)
            line_start = word_buffer[0][1]
            line_end = word_buffer[-1][2]
            lines = split_text_into_lines(text, max_chars_per_line)
            srt_text = "\n".join(lines)
            srt_lines.append(f"{index}\n{format_time(line_start)} --> {format_time(line_end)}\n{srt_text}\n")
            index += 1
            word_buffer = []

    # Catch any leftovers
    if word_buffer:
        text = " ".join(w for w, _, _ in word_buffer)
        line_start = word_buffer[0][1]
        line_end = word_buffer[-1][2]
        lines = split_text_into_lines(text, max_chars_per_line)
        srt_text = "\n".join(lines)
        srt_lines.append(f"{index}\n{format_time(line_start)} --> {format_time(line_end)}\n{srt_text}\n")

    srt_text = "\n".join(srt_lines) + "\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(srt_text)

def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def save_audio(base64_str: str, path: str):
    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_str))

def save_alignment(alignment, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(alignment.dict(), f, indent=2, ensure_ascii=False)

def generate_audio(text: str, outdir: str):
    audio = elevenlabs.text_to_speech.convert_with_timestamps(
        text=text,
        voice_id="nPczCjzI2devNBz1zQrb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    
    # Save audio
    audio_filename = os.path.join(output_dir, f"audio.mp3")
    save_audio(audio.audio_base_64, audio_filename)

    # Save raw alignment data for debugging/future use
    alignment_filename = os.path.join(output_dir,"alignment.json")
    save_alignment(audio.alignment, alignment_filename)

    return audio

# === ENTRY POINT ===
if __name__ == "__main__":
    input_path = "scripts.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[0])

    output_dir = s.title
    os.makedirs(output_dir, exist_ok=True)
    
    alignment_filename = os.path.join(output_dir,"alignment.json")
    audio = generate_audio(s.text, output_dir)
