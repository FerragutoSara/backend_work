from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.models.serializers import user_serializer

router = APIRouter(prefix="/users", tags=["users"])
repo = UserRepository()

@router.post("/")
def create_user(payload: UserCreate):
    user_id = repo.create_user(payload.model_dump())
    user = repo.get_user_by_id(user_id)
    return user_serializer(user)

@router.get("/")
def get_users():
    users = repo.get_all_users()
    return [user_serializer(user) for user in users]

@router.get("/{user_id}")
def get_user(user_id: str):
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_serializer(user)

@router.put("/{user_id}")
def update_user(user_id: str, payload: UserUpdate):
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    repo.update_user(user_id, update_data)
    updated_user = repo.get_user_by_id(user_id)
    return user_serializer(updated_user)

@router.delete("/{user_id}")
def delete_user(user_id: str):
    deleted = repo.delete_user(user_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}