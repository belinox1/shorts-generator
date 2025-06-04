import os
import json
from script_model import Script
from elevenlabs import CharacterAlignmentResponseModel
import logging

# === LOGGER SETUP ===
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def generate_subtitles_from_alignment(alignment, filename: str, max_chars=5):
    logger.info(f"Generation subtitles for {filename}")
    characters = alignment.characters
    starts = alignment.character_start_times_seconds
    ends = alignment.character_end_times_seconds

    subtitles = []
    index = 1
    word = ""
    word_start = None
    buffer = []

    def flush():
        nonlocal index, buffer
        if not buffer:
            return
        line = " ".join(w for w, _, _ in buffer).strip()
        start_time = buffer[0][1]
        end_time = buffer[-1][2]
        subtitles.append(f"{index}\n{format_time(start_time)} --> {format_time(end_time)}\n{line}\n")
        index += 1
        buffer.clear()

    for i, (char, start, end) in enumerate(zip(characters, starts, ends)):
        if char != " ":
            if not word:
                word_start = start
            word += char

        if char == " " or i == len(characters) - 1:
            if word:
                word_end = end
                buffer.append((word, word_start, word_end))

                current_line = " ".join(w for w, _, _ in buffer)
                if (
                    len(current_line) >= max_chars or
                    word.endswith((".", "?", "!"))
                ):
                    flush()
                word = ""

    flush()  # Final flush if anything remains

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(subtitles).replace("-", " ").replace("—", " — " ) + "\n")



if __name__ == "__main__":
    input_path = "stoicism.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    for script in scripts:    
        s = Script(**script)

        output_dir = s.title
        os.makedirs(output_dir, exist_ok=True)

        alignment_filename = os.path.join(output_dir, "alignment.json")
        with open(alignment_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            alignment = CharacterAlignmentResponseModel(**data)

        subtitle_filename = os.path.join(output_dir, f"subtitles.srt")
        generate_subtitles_from_alignment(alignment, subtitle_filename)
