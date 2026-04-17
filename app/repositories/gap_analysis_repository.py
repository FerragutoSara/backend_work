from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_GAP_ANALYSIS


class GapAnalysisRepository:
    def __init__(self):
        self.collection = get_database()[MONGO_COLLECTION_GAP_ANALYSIS]

    def create_gap_analysis(self, gap_analysis_data: dict) -> str:
        result = self.collection.insert_one(gap_analysis_data)
        return str(result.inserted_id)

    def get_by_user(self, user_id: str):
        """
        Ritorna tutte le analisi associate a uno user_id.
        """
        cursor = self.collection.find(
            {"analysis.user_id": user_id},
            {"_id": 0}
        )
        return list(cursor)

    def get_by_analysis_id(self, analysis_id: str):
        """
        Ritorna una singola analisi tramite analysis.id.
        """
        return self.collection.find_one(
            {"analysis.id": analysis_id},
            {"_id": 0}
        )
