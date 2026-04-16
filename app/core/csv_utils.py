import csv
from pathlib import Path
from typing import Dict, List, Optional

# Percorso assoluto alla cartella data/
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

class CSVDataLoader:
    """Utility per caricare e filtrare dati CSV da `skillbridge/data/`."""

    def __init__(self, filename: str):
        self.filename = filename
        self.path = DATA_DIR / filename

        if not self.path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.path}")

        self._rows = self._load_rows()

    def _load_rows(self) -> List[Dict[str, str]]:
        with self.path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [self._normalize_row(row) for row in reader]

    @staticmethod
    def _normalize_row(row: Dict[str, Optional[str]]) -> Dict[str, str]:
        return {key: (value or "") for key, value in row.items()}

    def all(self) -> List[Dict[str, str]]:
        return list(self._rows)

    def filter_by(self, field: str, value: str) -> List[Dict[str, str]]:
        return [row for row in self._rows if row.get(field) == value]

    def search_by(self, field: str, query: str) -> List[Dict[str, str]]:
        query_lower = query.strip().lower()
        return [
            row
            for row in self._rows
            if query_lower in (row.get(field, "").strip().lower())
        ]

    def search_with_keywords(self, field: str, query: str) -> List[Dict[str, str]]:
        query_tokens = [token for token in query.strip().lower().split() if token]
        if not query_tokens:
            return []

        results: List[Dict[str, str]] = []
        for row in self._rows:
            haystack = row.get(field, "").lower()
            if any(token in haystack for token in query_tokens):
                results.append(row)
        return results
