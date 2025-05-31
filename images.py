import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import logging
from script_model import Script

load_dotenv()

# === LOGGER SETUP ===
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

# === CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "dall-e-3"
IMAGE_SIZE = "1024x1792"
OUTPUT_DIR = "generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=OPENAI_API_KEY)

# === PROMPT GENERATOR ===
def build_prompt(script: Script, custom):
    return (
        f"You're creating an image for a YouTube Short.\n"
        f"The theme of the channel is {theme}\n\n"
        f"Details of the video:\n"
        f"Title: {script.title}\n"
        f"Script: {script.text}\n"
        f"The generated image should be vertical (9:16).\n"
        f"Don't include any text in the image.\n"
        f"{custom}"
    )

# === IMAGE GENERATOR ===
def generate_image(prompt, filename):
    logger.info(f"🎨 Generating image {filename}...")
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=IMAGE_SIZE,
        n=1,
        quality="standard"
    )
    url = response.data[0].url
    os.system(f"curl -s '{url}' -o '{filename}'")
    logger.info(f"✅ Saved: {filename}")
    time.sleep(1.2)  # Avoid rate limit

# === MAIN ===
def generate_all_images(script: Script, theme: str, customizations: list[str]):
    for i, c in enumerate(customizations):
        prompt = build_prompt(script, c)
        filename = os.path.join(OUTPUT_DIR, f"{script.title}_{i}.png")
        generate_image(prompt, filename)


if __name__ == "__main__":
    input_path = "stoic_shorts_bulk.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[3])
    theme = "stoicism"
    customizations = ["Use cinematic lighting, classic style. The image should be dynamic and eye catching.",
                      "Use dramatic lighting. Deep, enigmatic imagery to capture the meaning of the message.",
                      "Rich in details related to the theme. Build a narrative"]
    generate_all_images(s, theme, customizations)
