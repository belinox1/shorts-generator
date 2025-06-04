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
PROMPT_MODEL = "gpt-4.1"
MODEL = "dall-e-3"
IMAGE_SIZE = "1024x1792"

client = OpenAI(api_key=OPENAI_API_KEY)

# === PROMPT GENERATOR ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_image_prompts",
            "description": "Generate image prompts from scripts",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompts": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        }
                    }
                },
                "required": ["prompts"]
            }
        }
    }
]

def build_prompts(script: Script):
    logger.info("🚀 Generating Prompts...")

    # Create the chat completion request
    response = client.chat.completions.create(
        model=PROMPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a creative assistant helping generate DALL·E image prompts for YouTube Shorts. "
                    "Your goal is to create prompts based on a script:\n"
                    "Each prompt should describe a vertical, portrait, cinematic, visually compelling image, without any text or logos."
                    "The prompts must not refer directly to the script lines but instead visually represent the idea or emotion behind them."
                    "Each image will be prompted individually, so the prompts should not refer each other."
                    "Anyways, try to keep the images coherent to form a video." 
                    "Explore styles." 
                    "Be very descriptive to capture the mood and the theme right."
                )
            },
                        {
                "role": "user",
                "content": (
                    "Generate three prompts for this script:"
                    f"{script.model_dump_json()}"
                )
            }
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "generate_image_prompts"}}
    )

    # Extract the function call arguments
    try:
        tool_response = response.choices[0].message.tool_calls[0].function
        prompts = json.loads(tool_response.arguments)["prompts"]
    except Exception as e:
        logger.error("❌ Failed to parse scripts:")
        logger.error(json.dumps(response.model_dump(), indent=2))
        raise e
    
    return prompts

# === IMAGE GENERATOR ===
def generate_image(prompt, filename):
    logger.info(f"🎨 Generating image {filename}...")
    logger.info(f"{prompt}")
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
def generate_all_images(script: Script):
    output_dir = script.title
    os.makedirs(output_dir, exist_ok=True)
    prompts = build_prompts(script)
    for i, prompt in enumerate(prompts):
        filename = os.path.join(output_dir, f"{i}.png")
        generate_image(prompt, filename)


if __name__ == "__main__":
    input_path = "stoicism.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scripts = json.load(f)
    s = Script(**scripts[7])
    generate_all_images(s)
