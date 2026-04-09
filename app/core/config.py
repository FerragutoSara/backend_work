import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "users-crud")
MONGO_COLLECTION_USERS = os.getenv("MONGO_COLLECTION_USERS", "users")
MONGO_COLLECTION_AUTH = os.getenv("MONGO_COLLECTION_AUTH", "auth")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret-token-key")

if not MONGO_URI:
    raise ValueError("MONGO_URI non configurata nel file .env")