import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/shortener")
SECRET_KEY_EMAIL = os.getenv("SECRET_KEY_EMAIL")
SECRET_KEY_TELEGRAM = os.getenv("SECRET_KEY_TELEGRAM")
ALGORITHM = "HS256"