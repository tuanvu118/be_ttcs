# configs/cloudinary.py
import os
import cloudinary
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # project root (tùy cấu trúc)
load_dotenv(BASE_DIR / ".env")

CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "").strip()

def init_cloudinary() -> None:
    cloud_name = os.getenv("CLOUDINARY_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")


    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )
