import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()


client = InferenceClient(
    provider="fal-ai",
    api_key=os.getenv("HF_TOKEN"),
)


def generate_image(prompt):
    if not os.getenv("HF_TOKEN"):
        raise ValueError("HF_TOKEN is missing. Add it to .env to enable image generation.")

    image = client.text_to_image(
        prompt,
        model="stabilityai/stable-diffusion-xl-base-1.0",
    )

    return image
