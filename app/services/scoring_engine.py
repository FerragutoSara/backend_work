from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE_DIR = os.path.normpath(BASE_DIR)

# categorie canoniche interne
CANONICAL_CATEGORIES = ("linguaggi", "software", "framework", "knowledge")

# mappatura CSV → categorie canoniche
CATEGORY_MAP = {
    "Language": "linguaggi",
    "software": "software",
    "framework": "framework",
    "knowledge": "knowledge",
}


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def _read_csv_dicts(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _as_int(v: str) -> int:
    return int(v.strip())


def _as_float(v: str) -> float:
    return float(v.strip())


def _round(x: float, ndigits: int) -> float:
    return round(float(x), ndigits)


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _analysis_id(user_id: str) -> str:
    now = datetime.now().astimezone()
    return f"ana_{now:%Y%m%d_%H%M%S}_{user_id}"


def _compatibility_label(score: float) -> str:
    if score <= 0.24:
        return "non compatibile"
    if score <= 0.49:
        return "compatibilità bassa"
    if score <= 0.69:
        return "parzialmente allineato"
    if score <= 0.84:
        return "vicino al ruolo"
    return "fortemente compatibile"


def _expected_level_label(expected_level: float) -> str:
    if expected_level >= 0.90:
        return "Conoscenza esperta"
    if expected_level >= 0.80:
        return "Conoscenza avanzata"
    if expected_level >= 0.65:
        return "Conoscenza solida"
    if expected_level >= 0.50:
        return "Conoscenza di base"
    return "Conoscenza consapevole"


# ---------------------------------------------------------
# Data structures
# ---------------------------------------------------------

@dataclass(frozen=True)
class RoleRequirement:
    role_id: int
    skill_id: int
    category: str
    weight: float
    expected_level: float   # scala 0–1
    is_critical: bool
    threshold: float        # scala 0–1
    penalty: float


# ---------------------------------------------------------
# Catalog
# ---------------------------------------------------------

class Catalog:
    def __init__(self, base_dir: str = BASE_DIR) -> None:
        self.base_dir = base_dir
        self._skills_by_id = {}
        self._job_by_id = {}
        self._area_by_id = {}
        self._requirements_by_role = {}
        self._load()

    def _load(self) -> None:
        # skills.csv
        skills_path = os.path.join(self.base_dir, "data", "skills.csv")
        for row in _read_csv_dicts(skills_path):
            sid = _as_int(row["id"])
            raw_cat = row["type"].strip().lower()
            mapped_cat = CATEGORY_MAP.get(raw_cat, raw_cat)

            self._skills_by_id[sid] = {
                "skill_id": sid,
                "skill_name": row["skill"],
                "category": mapped_cat,
            }

        # job_title.csv
        job_path = os.path.join(self.base_dir, "data", "job_title.csv")
        for row in _read_csv_dicts(job_path):
            jid = _as_int(row["id"])
            self._job_by_id[jid] = {
                "job_id": jid,
                "job_title": row["job_title"],
                "area_id": row["id_area"],
            }

        # area.csv
        area_path = os.path.join(self.base_dir, "data", "area.csv")
        for row in _read_csv_dicts(area_path):
            aid = row["id"].strip()
            self._area_by_id[aid] = {"area_id": aid, "area_name": row["area"]}

        # role_skills_requirements.csv
        req_path = os.path.join(self.base_dir, "data", "role_skills_requirements.csv")
        for row in _read_csv_dicts(req_path):
            role_id = _as_int(row["role_id"])
            req = RoleRequirement(
                role_id=role_id,
                skill_id=_as_int(row["skill_id"]),
                category=row["category"].strip().lower(),
                weight=_as_float(row["weight_normalized"]),
                expected_level=_as_float(row["expected_level"]),  # 0–1
                is_critical=row["is_critical"].strip().lower() == "true",
                threshold=_as_float(row["threshold"]),            # 0–1
                penalty=_as_float(row["penalty"]),
            )
            self._requirements_by_role.setdefault(role_id, []).append(req)

    def get_skill(self, skill_id: int) -> Dict[str, Any]:
        return self._skills_by_id[skill_id]

    def get_job(self, job_id: int) -> Dict[str, Any]:
        return self._job_by_id[job_id]

    def get_area_name(self, area_id: str) -> str:
        return self._area_by_id[area_id]["area_name"]

    def get_requirements(self, role_id: int) -> List[RoleRequirement]:
        return list(self._requirements_by_role.get(role_id, []))


# ---------------------------------------------------------
# Input validation
# ---------------------------------------------------------

def _validate_input(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload.get("user_id"), str):
        raise ValueError("Missing or invalid user_id")

    target = payload.get("target")
    if not isinstance(target, dict):
        raise ValueError("Missing or invalid target")

    if not isinstance(target.get("area_id"), str):
        raise ValueError("Missing or invalid target.area_id")

    if not isinstance(target.get("job_id"), int):
        raise ValueError("Missing or invalid target.job_id")

    skills = payload.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ValueError("Missing or invalid skills")

    seen = set()
    for s in skills:
        if not isinstance(s, dict):
            raise ValueError("Invalid skill entry")
        sid = s.get("skill_id")
        if not isinstance(sid, int):
            raise ValueError("Invalid skill_id")
        if sid in seen:
            raise ValueError(f"Duplicated skill_id={sid}")
        seen.add(sid)
        ul = s.get("user_level")
        if not isinstance(ul, int) or not (0 <= ul <= 10):
            raise ValueError(f"Invalid user_level for skill_id={sid}")


# ---------------------------------------------------------
# GAP ANALYSIS ENGINE (VERSIONE FINALE)
# ---------------------------------------------------------

def run_gap_analysis(
    payload: Mapping[str, Any],
    *,
    catalog: Optional[Catalog] = None,
    consent_level: Optional[int] = None,
) -> Dict[str, Any]:

    _validate_input(payload)
    if catalog is None:
        catalog = Catalog()

    user_id = payload["user_id"]
    if consent_level is None:
        consent_level = payload.get("consent_level")
    if consent_level not in (1, 2):
        raise ValueError("Invalid consent_level")

    area_id = payload["target"]["area_id"]
    job_id = payload["target"]["job_id"]

    job = catalog.get_job(job_id)
    if job["area_id"] != area_id:
        raise ValueError("Target mismatch")

    requirements = catalog.get_requirements(job_id)
    if not requirements:
        raise ValueError(f"No requirements for job_id={job_id}")

    user_levels = {s["skill_id"]: s["user_level"] for s in payload["skills"]}

    skills_analysis = []
    total_weight = sum(r.weight for r in requirements)

    coverage_score = 0.0
    penalty_sum = 0.0

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------

    for req in requirements:
        user_level = user_levels.get(req.skill_id, 0)

        # expected_level è 0–1 → convertiamo a scala 0–10
        expected_10 = req.expected_level * 10

        # gap in scala 0–10
        gap = max(0, expected_10 - user_level)

        # coverage pesato
        coverage_score += req.weight * (user_level / 10)

        # penalty
        if req.is_critical and (user_level / 10) < req.threshold:
            penalty_sum += req.penalty

        skill_meta = catalog.get_skill(req.skill_id)

        skills_analysis.append({
            "skill_id": req.skill_id,
            "skill_name": skill_meta["skill_name"],
            "category": skill_meta["category"],
            "user_level": user_level,
            "expected_level": req.expected_level,  # 0–1
            "gap": gap,
            "weight": req.weight,
            "priority_score": req.weight * (gap / 10),
        })

    # ---------------------------------------------------------
    # METRICHE FINALI
    # ---------------------------------------------------------

    coverage_score /= total_weight
    penalty_sum = min(1.0, penalty_sum / total_weight)
    score_final = max(0.0, coverage_score - penalty_sum)

    # ordina per priorità
    skills_analysis.sort(key=lambda x: x["priority_score"], reverse=True)

    # ---------------------------------------------------------
    # PERCENTUALI coverage/gap (user_level + gap = 100%)
    # ---------------------------------------------------------

    skills_light = []
    for s in skills_analysis:
        ul = s["user_level"]
        gap = s["gap"]
        tot = ul + gap

        if tot == 0:
            coverage_pct = 0
            gap_pct = 100
        else:
            coverage_pct = round((ul / tot) * 100)
            gap_pct = round((gap / tot) * 100)

        skills_light.append({
            "skill_name": s["skill_name"],
            "user_level_pct": coverage_pct,
            "gap_pct": gap_pct,
        })

    # ---------------------------------------------------------
    # TRAINING PRIORITIES (TOP 5)
    # ---------------------------------------------------------

    training_light = []
    for s in skills_analysis:
        if s["gap"] <= 0:
            continue

        ul = s["user_level"]
        gap = s["gap"]
        tot = ul + gap
        gap_pct = round((gap / tot) * 100) if tot > 0 else 100

        training_light.append({
            "skill_name": s["skill_name"],
            "priority_score": s["priority_score"],
            "gap_pct": gap_pct,
            "expected_level": _expected_level_label(s["expected_level"]),
        })

        if len(training_light) >= 5:
            break

    # ---------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------

    return {
        "analysis": {
            "id": _analysis_id(user_id),
            "timestamp": _iso_now(),
            "user_id": user_id,
        },
        "target": {
            "job_id": job_id,
            "job_title": job["job_title"],
            "area_name": catalog.get_area_name(area_id),
        },
        "summary": {
            "coverage_score": _round(coverage_score, 2),
            "compatibility": _compatibility_label(score_final),
        },
        "skills": skills_light,
        "training_priorities": training_light,
    }
