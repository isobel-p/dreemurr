from dreemurr.utils import encode
import os
from openrouter import OpenRouter
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
DEFAULT_MODEL = "google/gemini-3.5-flash-lite"
prompt = ""

def generate(path:str, model:str) -> str:
    image = encode(path)

    client = OpenRouter(
        api_key=API_KEY,
        server_url="https://ai.hackclub.com/proxy/v1", # TODO make this configurable via config file
    )

    if "prompt" not in globals():
        with open("prompt.txt") as f:
            prompt = f.read()
            
    try:
        response = client.chat.send(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Generate a filename for this image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
                ]}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        from datetime import datetime
        return f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_dreemurr"