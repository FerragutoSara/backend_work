import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "skillbridge-db")
MONGO_COLLECTION_USERS = os.getenv("MONGO_COLLECTION_USERS", "users")
MONGO_COLLECTION_AUTH = os.getenv("MONGO_COLLECTION_AUTH", "auth")
MONGO_COLLECTION_USER_SKILLS = os.getenv("MONGO_COLLECTION_USER_SKILLS", "user_skills")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret-token-key")

if not MONGO_URI:
    raise ValueError("MONGO_URI non configurata nel file .env")