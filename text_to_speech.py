import os
import json
import base64
import logging
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from script_model import Script

load_dotenv()

# === LOGGER SETUP ===
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def save_audio(base64_str: str, path: str):
    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_str))

def save_alignment(alignment, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(alignment.dict(), f, indent=2, ensure_ascii=False)

def generate_audio(text: str, output_dir: str):
    logger.info(f"🔊 Generating audio for {output_dir}...")
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
    for script in scripts:
        s = Script(**script)

        output_dir = s.title
        os.makedirs(output_dir, exist_ok=True)
        
        alignment_filename = os.path.join(output_dir,"alignment.json")
        audio = generate_audio(s.text, output_dir)
