from fastapi import APIRouter, HTTPException
from app.schemas.user_skill_schema import UserSkillInput
from app.services.user_skill_service import UserSkillService

router = APIRouter(prefix="/user-skills", tags=["user-skills"])
service = UserSkillService()

@router.post("/")
def create_user_skills(payload: UserSkillInput):
    try:
        skill_id = service.validate_and_save_user_skills(payload)
        return {"message": "User skills salvate con successo", "id": skill_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")