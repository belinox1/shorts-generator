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

def generate_audio(text: str, filename: str):
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id="nPczCjzI2devNBz1zQrb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    save(audio, filename)
    return audio

# === ENTRY POINT ===
if __name__ == "__main__":
    input_path = "scripts.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[0])

    output_dir = s.title
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"audio.mp3")

    audio = generate_audio(s.text, filename)    