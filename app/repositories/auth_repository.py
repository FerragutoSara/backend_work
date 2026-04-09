from bson import ObjectId
from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_AUTH


class AuthRepository:
    def __init__(self):
        self.collection = get_database()[MONGO_COLLECTION_AUTH]

    def create_user(self, user_data: dict) -> str:
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def get_user_by_email(self, email: str):
        return self.collection.find_one({"email": email})

    def get_user_by_id(self, user_id: str):
        return self.collection.find_one({"_id": ObjectId(user_id)})
