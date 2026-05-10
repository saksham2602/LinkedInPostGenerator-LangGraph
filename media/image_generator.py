import os

from huggingface_hub import InferenceClient
from dotenv import load_dotenv


load_dotenv()


client = InferenceClient(
    provider="fal-ai",
    api_key=os.getenv("HF_TOKEN"),
)


def generate_image(prompt):

    image = client.text_to_image(
        prompt,
        model="stabilityai/stable-diffusion-xl-base-1.0",
    )

    return image