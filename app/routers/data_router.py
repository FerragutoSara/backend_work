from fastapi import APIRouter, HTTPException
from pathlib import Path
from app.core.csv_utils import CSVDataLoader, DATA_DIR

router = APIRouter()

# Usa direttamente DATA_DIR definito in csv_utils.py
skills_loader = CSVDataLoader("skills.csv")


router = APIRouter(prefix="/data", tags=["data"])

data_dir = Path(__file__).resolve().parents[2] / "data"
general_data_dir = Path(__file__).resolve().parents[2] / "general_data"
areas_loader = CSVDataLoader("area.csv")
skills_loader = CSVDataLoader("skills.csv")
job_titles_loader = CSVDataLoader("job_title.csv")
role_skills_loader = CSVDataLoader("role_skills_requirements.csv")



@router.get("/areas")
def get_areas():
    return areas_loader.all()


@router.get("/job_titles")
def get_job_titles(area_id: str | None = None):
    if area_id:
        return job_titles_loader.filter_by("id_area", str(area_id))
    return job_titles_loader.all()




@router.get("/skills/{role_id}")
def get_role_skills(role_id: str):
    # 1. Trova tutte le righe che collegano role → skill
    mappings = role_skills_loader.filter_by("role_id", role_id)

    if not mappings:
        return []

    # 2. Estrai gli ID delle skill richieste
    skill_ids = {m["skill_id"] for m in mappings}

    # 3. Recupera tutte le skill dal CSV principale
    all_skills = skills_loader.all()

    # 4. Filtra solo quelle richieste dal jobtitle
    result = [
        {
            "id": s["id"],
            "skill": s["skill"],
            "type": s["type"]
        }
        for s in all_skills
        if s["id"] in skill_ids
    ]

    return result



