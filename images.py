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
def build_prompt(script: Script, part, custom):
    return (
        f"You're creating an image for a YouTube Short.\n\n"
        f"Full script context:\n"
        f"Title: {script.title}\n"
        f"Hook: {script.hook}\n"
        f"Body: {script.body}\n"
        f"Close: {script.close}\n\n"
        f"Now generate a vertical (9:16) image that visually illustrates the following part:\n"
        f"{part}\n\n"
        f"{custom}"
    )

# === IMAGE GENERATOR ===
def generate_image(prompt, filename):
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=IMAGE_SIZE,
        n=1,
        quality="standard"
    )
    url = response.data[0].url
    os.system(f"curl -s '{url}' -o '{filename}'")
    time.sleep(1.2)  # Avoid rate limit

# === MAIN ===
def generate_all_images(script: Script):
    base = script.title
    hook_custom = "Use cinematic lighting, classic style. The image should be dynamic and eye catching."
    prompt = build_prompt(script, script.hook, hook_custom)
    filename = os.path.join(OUTPUT_DIR, f"{base}_hook.png")
    print(f"🎨 Generating hook image for {base}...")
    generate_image(prompt, filename)
    logger.info(f"✅ Saved: {filename}")

if __name__ == "__main__":
    input_path = "scripts.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[0])
    generate_all_images(s)
