from fastapi import HTTPException
from app.repositories.gap_analysis_repository import GapAnalysisRepository


class GapAnalysisService:
    def __init__(self):
        self.repo = GapAnalysisRepository()

    def create_gap_analysis(self, gap_analysis_data: dict) -> str:
        """
        Salva una nuova analisi nel DB.
        """
        return self.repo.create_gap_analysis(gap_analysis_data)

    def get_gap_analysis_by_user(self, user_id: str):
        """
        Recupera tutte le analisi associate a uno user_id.
        """
        results = self.repo.get_by_user(user_id)
        if not results:
            raise HTTPException(status_code=404, detail="No analyses found for this user")
        return results

    def get_gap_analysis_by_id(self, analysis_id: str):
        """
        Recupera una singola analisi tramite analysis.id.
        """
        result = self.repo.get_by_analysis_id(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return result
