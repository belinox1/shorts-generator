import os
import json
from openai import OpenAI
from pydantic import BaseModel
import logging

# === CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1" 

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
# === MODEL DEFINITION ===
class Script(BaseModel):
    title: str
    hook: str
    body: str
    close: str

    @property
    def text(self):
        return f"{self.hook} {self.body} {self.close}"

# === MAIN LOGIC ===
def generate_scripts(theme: str, custom_instructions: str):
    logger.info("🚀 Generating Scripts...")

    # Create the chat completion request
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate ten unique {theme} themed YouTube Shorts scripts."
                    "Aim for about 20s at moderate reading speed."
                    "Each script should include: title, hook, body, and close."
                    "In hook catch the attention."
                    "In value bring value."
                    "In close always call to action."
                    "Format them using the generate_short_scripts function. "
                    f"{custom_instructions}"
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
    output_path = "stoic_shorts_bulk.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ All scripts saved to '{output_path}'")

    return [Script(**data) for data in scripts]

# === ENTRY POINT ===
if __name__ == "__main__":
    client = OpenAI(api_key=OPENAI_API_KEY) # Initilize client
    theme = "stoicism"
    custom_isntructions = "Make them engaging and educative. Aim for viral potential."
    scripts = generate_scripts(theme, custom_isntructions)
