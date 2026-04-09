from pymongo import MongoClient
from app.core.config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
database = client[MONGO_DB]

def get_database():
    return database