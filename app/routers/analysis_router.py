from fastapi import APIRouter
from app.services.gap_analysis_service import GapAnalysisService

router = APIRouter(prefix="/gap_analysis", tags=["Gap Analysis"])
service = GapAnalysisService()


@router.get("/{user_id}")
def get_gap_analysis_by_user(user_id: str):
    return service.get_gap_analysis_by_user(user_id)