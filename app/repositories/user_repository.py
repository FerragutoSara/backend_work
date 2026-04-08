from bson import ObjectId
from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_USERS

class UserRepository:
    def __init__(self):
        self.collection = get_database()[MONGO_COLLECTION_USERS]

    def create_user(self, user_data: dict) -> str:
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def get_all_users(self):
        return list(self.collection.find())

    def get_user_by_id(self, user_id: str):
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def update_user(self, user_id: str, update_data: dict) -> int:
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete_user(self, user_id: str) -> int:
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count