import os
from dotenv import load_dotenv

load_dotenv()
print(f"GOOGLE_REDIRECT_URI: {os.getenv('GOOGLE_REDIRECT_URI')}")
