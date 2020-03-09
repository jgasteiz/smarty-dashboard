import os

from dotenv import load_dotenv

load_dotenv()

SMARTY_EMAIL = os.environ.get("EMAIL", "")
SMARTY_PASSWORD = os.environ.get("PASSWORD", "")
