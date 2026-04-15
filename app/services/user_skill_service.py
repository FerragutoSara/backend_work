from app.repositories.user_skill_repository import UserSkillRepository
from app.core.csv_utils import CSVDataLoader
from app.schemas.user_skill_schema import UserSkillInput
from fastapi import HTTPException
import os
from pathlib import Path

class UserSkillService:
    def __init__(self):
        self.repo = UserSkillRepository()
        # Usa general_data per skills.csv
        general_data_dir = Path(__file__).resolve().parents[2] / "general_data"
        self.skills_loader = CSVDataLoader("skills.csv", data_dir=general_data_dir)

    def validate_and_save_user_skills(self, user_skill_data: UserSkillInput) -> str:
        # Validazione: controllare se skill_id esistono
        all_skills = self.skills_loader.all()
        skill_ids = {int(skill.get('id', 0)) for skill in all_skills if skill.get('id')}

        for skill in user_skill_data.skills:
            if skill.skill_id not in skill_ids:
                raise HTTPException(status_code=400, detail=f"Skill ID {skill.skill_id} non valida")

            if not (0 <= skill.user_level <= 10):
                raise HTTPException(status_code=400, detail=f"User level {skill.user_level} deve essere tra 0 e 10")

        # Salva nel DB
        data_to_save = user_skill_data.model_dump()
        skill_id = self.repo.create_user_skill(data_to_save)
        return skill_id