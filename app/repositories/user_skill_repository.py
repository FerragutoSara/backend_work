from bson import ObjectId
from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_USER_SKILLS

class UserSkillRepository:
    def __init__(self):
        self.collection = get_database()[MONGO_COLLECTION_USER_SKILLS]

    def create_user_skill(self, user_skill_data: dict) -> str:
        result = self.collection.insert_one(user_skill_data)
        return str(result.inserted_id)

    def get_user_skills_by_user_id(self, user_id: str):
        return list(self.collection.find({"user_id": user_id}))

    def get_user_skill_by_id(self, skill_id: str):
        return self.collection.find_one({"_id": ObjectId(skill_id)})

    def update_user_skill(self, skill_id: str, update_data: dict) -> int:
        result = self.collection.update_one(
            {"_id": ObjectId(skill_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete_user_skill(self, skill_id: str) -> int:
        result = self.collection.delete_one({"_id": ObjectId(skill_id)})
        return result.deleted_count