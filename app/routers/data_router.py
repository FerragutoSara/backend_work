from fastapi import APIRouter, HTTPException
from app.core.csv_utils import CSVDataLoader

router = APIRouter(prefix="/data", tags=["data"])

areas_loader = CSVDataLoader("area.csv")
job_titles_loader = CSVDataLoader("job_title.csv")
skills_loader = CSVDataLoader("skills.csv")


@router.get("/areas")
def get_areas():
    return areas_loader.all()


@router.get("/job_titles")
def get_job_titles(area_id: str | None = None):
    if area_id:
        return job_titles_loader.filter_by("id_area", area_id)
    return job_titles_loader.all()


@router.get("/job_titles/area/{area_id}")
def get_job_titles_by_area(area_id: str):
    results = job_titles_loader.filter_by("id_area", area_id)
    if not results:
        raise HTTPException(status_code=404, detail=f"Nessuna job title trovata per l'area {area_id}")
    return results


@router.get("/skills")
def get_skills(job_title_id: str | None = None, job_title: str | None = None):
    if job_title_id:
        job_titles = job_titles_loader.filter_by("id", job_title_id)
        if not job_titles:
            raise HTTPException(status_code=404, detail=f"Job title non trovata: {job_title_id}")
        title_name = job_titles[0].get("job_title", "")
        return skills_loader.search_with_keywords("skill", title_name)

    if job_title:
        return skills_loader.search_with_keywords("skill", job_title)

    return skills_loader.all()


@router.get("/skills/job_title/{job_title_id}")
def get_skills_by_job_title(job_title_id: str):
    job_titles = job_titles_loader.filter_by("id", job_title_id)
    if not job_titles:
        raise HTTPException(status_code=404, detail=f"Job title non trovata: {job_title_id}")
    title_name = job_titles[0].get("job_title", "")
    results = skills_loader.search_with_keywords("skill", title_name)
    if not results:
        raise HTTPException(status_code=404, detail=f"Nessuna skill trovata per la job title {title_name}")
    return results
