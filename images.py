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

client = OpenAI(api_key=OPENAI_API_KEY)

# === PROMPT GENERATOR ===
def build_prompt(script: Script, custom):
    return (
        f"{custom}"
        f"{script.title}\n"
        f"{script.hook}\n"
        f"{script.body}\n"
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
def generate_all_images(script: Script, customizations: list[str]):
    output_dir = script.title
    os.makedirs(output_dir, exist_ok=True)
    for i, c in enumerate(customizations):
        prompt = build_prompt(script, c)
        filename = os.path.join(output_dir, f"{i}.png")
        generate_image(prompt, filename)


if __name__ == "__main__":
    input_path = "stoic_shorts_bulk.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[7])
    customizations = ["Use cinematic lighting, classic style. The image should be dynamic and eye catching.",
                      "Use cinematic lighting, abstract style. The image should be thought provoking.",
                      "Use cinematic lighting, modern style. The image is inspiring."]
    generate_all_images(s, customizations)
