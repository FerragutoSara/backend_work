from app.db.mongodb import get_database
from app.core.config import MONGO_COLLECTION_GAP_ANALYSIS


class GapAnalysisRepository:
    def __init__(self):
        self.collection = get_database()[MONGO_COLLECTION_GAP_ANALYSIS]

    def create_gap_analysis(self, gap_analysis_data: dict) -> str:
        result = self.collection.insert_one(gap_analysis_data)
        return str(result.inserted_id)
