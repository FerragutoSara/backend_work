from app.repositories.user_skill_repository import UserSkillRepository
from app.repositories.gap_analysis_repository import GapAnalysisRepository
from app.core.csv_utils import CSVDataLoader, DATA_DIR
from app.schemas.user_skill_schema import UserSkillInput
from app.services.scoring_engine import run_gap_analysis
from fastapi import HTTPException


class UserSkillService:
    def __init__(self):
        self.repo = UserSkillRepository()
        self.gap_analysis_repo = GapAnalysisRepository()

        # Carica skills.csv dalla cartella corretta: skillbridge/data/
        self.skills_loader = CSVDataLoader("skills.csv")

        # oppure semplicemente:
        # self.skills_loader = CSVDataLoader("skills.csv")

    def validate_and_save_user_skills(self, user_skill_data: UserSkillInput) -> tuple[str, dict]:
        # Validazione: controllare se skill_id esistono
        all_skills = self.skills_loader.all()
        skill_ids = {int(skill.get('id', 0)) for skill in all_skills if skill.get('id')}

        for skill in user_skill_data.skills:
            if skill.skill_id not in skill_ids:
                raise HTTPException(status_code=400, detail=f"Skill ID {skill.skill_id} non valida")

            if not (0 <= skill.user_level <= 10):
                raise HTTPException(status_code=400, detail=f"User level {skill.user_level} deve essere tra 0 e 10")

        # Calcola lo scoring prima di salvare
        data_to_save = user_skill_data.model_dump()
        consent_level = user_skill_data.consent_level or 1

        try:
            analysis = run_gap_analysis(data_to_save, consent_level=consent_level)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        data_to_save["analysis"] = analysis
        skill_id = self.repo.create_user_skill(data_to_save)

        gap_analysis_data = {**analysis, "user_skill_id": skill_id}
        self.gap_analysis_repo.create_gap_analysis(gap_analysis_data)

        return skill_id, analysis
