import os
import json
from openai import OpenAI
import logging
from dotenv import load_dotenv
from script_model import Script  

load_dotenv()

# === CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1" 
client = OpenAI(api_key=OPENAI_API_KEY) # Initilize client

# === LOGGER SETUP ===
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

# === TOOL DEFINITION ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_short_scripts",
            "description": "Generate short video scripts",
            "parameters": {
                "type": "object",
                "properties": {
                    "scripts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "theme": {"type": "string"},
                                "title": {"type": "string"},
                                "hook": {"type": "string"},
                                "body": {"type": "string"},
                                "close": {"type": "string"}
                            },
                            "required": ["title", "hook", "body", "close"]
                        }
                    }
                },
                "required": ["scripts"]
            }
        }
    }
]

# === MAIN LOGIC ===
def generate_scripts(theme: str, custom_instructions: str):
    logger.info("🚀 Generating Scripts...")

    # Create the chat completion request
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a creative assistant helping me create scripts for YouTube Shorts."
                    "For each script aim for about 30s at moderate reading speed."
                    "Each script should include: title, hook, body, and close."
                    "In hook catch the attention."
                    "In body bring value."
                    "In close always call to action."
                    "Format them using the generate_short_scripts function. "
                    f"{custom_instructions}"
                )
            },
                        {
                "role": "user",
                "content": (
                    f"Generate ten scripts with the theme {theme}"
                )
            }
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "generate_short_scripts"}}
    )

    # Extract the function call arguments
    try:
        tool_response = response.choices[0].message.tool_calls[0].function
        scripts = json.loads(tool_response.arguments)["scripts"]
    except Exception as e:
        logger.error("❌ Failed to parse scripts:")
        logger.error(json.dumps(response.model_dump(), indent=2))
        raise e

    # Save the scripts to a file
    output_path = "scripts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ All scripts saved to '{output_path}'")

    return [Script(**data) for data in scripts]

# === ENTRY POINT ===
if __name__ == "__main__":
    theme = "philosophy"
    custom_instructions = "Make them deep and meaningful. Aim for viral potential."
    scripts = generate_scripts(theme, custom_instructions)

    logger.info("\n📝 Script outputs:")
    for i, s in enumerate(scripts):
        logger.info(f"\n🎬 Script {i}: {s.title}\n{s.text}")
