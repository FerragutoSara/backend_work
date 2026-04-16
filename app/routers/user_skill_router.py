from fastapi import APIRouter, HTTPException
from app.schemas.user_skill_schema import UserSkillInput
from app.services.user_skill_service import UserSkillService
import traceback

router = APIRouter(prefix="/user-skills", tags=["user-skills"])
service = UserSkillService()

from datetime import datetime, timezone

@router.post("/")
def create_user_skills(payload: UserSkillInput):
    try:
        if payload.timestamp is None:
            payload.timestamp = datetime.now(timezone.utc)

        print("PAYLOAD ARRIVATO:", payload.model_dump())

        skill_id, analysis = service.validate_and_save_user_skills(payload)

        return {
            "message": "User skills salvate con successo",
            "id": skill_id,
            "analysis": analysis,
        }

    except Exception as e:
        print("ERRORE INTERNO:", repr(e))
        traceback.print_exc()   # <--- AGGIUNGILO
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")



