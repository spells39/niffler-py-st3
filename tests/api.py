from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("BASE_URL")
token = os.getenv("TOKEN")