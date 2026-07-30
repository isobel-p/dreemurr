from dreemurr.utils import encode
import os
from openrouter import OpenRouter
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
DEFAULT_MODEL = "google/gemini-3.5-flash-lite"


def generate(path:str, model:str) -> str:
    image = encode(path)

    client = OpenRouter(
        api_key=API_KEY,
        server_url="https://ai.hackclub.com/proxy/v1",
    )

    with open("prompt.txt") as f:
        prompt = f.read()

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
    print(response.choices[0].message.content)
    return response.choices[0].message.content