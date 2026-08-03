from dreemurr.utils import encode
import os
from openrouter import OpenRouter
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")
DEFAULT_MODEL = "google/gemini-3.5-flash-lite"
PROMPT = "You are an AI assistant that generates descriptive filenames for images. Output ONLY the filename, 3-5 words, lowercase, underscores_between_words. No extra text, no quotes, no markdown. Be as detailed as possible."

def generate(path:str, model:str) -> str:
    image = encode(path)

    client = OpenRouter(
        api_key=API_KEY,
        server_url="https://ai.hackclub.com/proxy/v1", # TODO make this configurable via config file
    )

    try:
        response = client.chat.send(
            model=model,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": "Generate a filename for this image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
                ]}
            ],
        )
        result = response.choices[0].message.content
        if not result or not result.strip():
            raise ValueError("Empty AI response")
        return result
    except Exception as e:
        log_path = Path.home() / ".dreemurr_error.log"
        with open(log_path, "a") as f:
            f.write(f"{datetime.now()}: {e}\n")
        return f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_dreemurr"