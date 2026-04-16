from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE_DIR = os.path.normpath(BASE_DIR)


CANONICAL_CATEGORIES = ("linguaggi", "software", "framework", "knowledge")


def _read_csv_dicts(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _as_int(value: str) -> int:
    return int(value.strip())


def _as_float(value: str) -> float:
    return float(value.strip())


def _round(x: float, ndigits: int) -> float:
    return round(float(x), ndigits)


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _analysis_id(user_id: str) -> str:
    now = datetime.now().astimezone()
    return f"ana_{now:%Y%m%d_%H%M%S}_{user_id}"


def _compatibility_label(score_final: float) -> str:
    if score_final <= 0.24:
        return "non compatibile"
    if score_final <= 0.49:
        return "compatibilità bassa"
    if score_final <= 0.69:
        return "parzialmente allineato"
    if score_final <= 0.84:
        return "vicino al ruolo"
    return "fortemente compatibile"


def _category_status(score: float) -> str:
    if score >= 0.75:
        return "forte"
    if score >= 0.45:
        return "intermedia"
    return "debole"


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


@dataclass(frozen=True)
class RoleRequirement:
    role_id: int
    skill_id: int
    category: str
    weight: float
    expected_level: float
    is_critical: bool
    threshold: float
    penalty: float


class Catalog:
    def __init__(self, base_dir: str = BASE_DIR) -> None:
        self.base_dir = base_dir

        self._skills_by_id: Dict[int, Dict[str, Any]] = {}
        self._job_by_id: Dict[int, Dict[str, Any]] = {}
        self._area_by_id: Dict[str, Dict[str, Any]] = {}
        self._requirements_by_role: Dict[int, List[RoleRequirement]] = {}

        self._load()

    def _load(self) -> None:
        # 🔴 PRIMA: "csv" → ORA: "data"
        skills_path = os.path.join(self.base_dir, "data", "skills.csv")
        for row in _read_csv_dicts(skills_path):
            sid = _as_int(row["id"])
            self._skills_by_id[sid] = {
                "skill_id": sid,
                "skill_name": row["skill"],
                "category": row["type"],
            }

        job_path = os.path.join(self.base_dir, "data", "job_title.csv")
        for row in _read_csv_dicts(job_path):
            jid = _as_int(row["id"])
            self._job_by_id[jid] = {
                "job_id": jid,
                "job_title": row["job_title"],
                "area_id": row["id_area"],
            }

        area_path = os.path.join(self.base_dir, "data", "area.csv")
        for row in _read_csv_dicts(area_path):
            aid = row["id"].strip()
            self._area_by_id[aid] = {"area_id": aid, "area_name": row["area"]}

        req_path = os.path.join(self.base_dir, "data", "role_skill_requirement.csv")
        for row in _read_csv_dicts(req_path):
            role_id = _as_int(row["role_id"])
            req = RoleRequirement(
                role_id=role_id,
                skill_id=_as_int(row["skill_id"]),
                category=row["category"].strip(),
                weight=_as_float(row["weight_normalized"]),
                expected_level=_as_float(row["expected_level"]),
                is_critical=row["is_critical"].strip().lower() == "true",
                threshold=_as_float(row["threshold"]),
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


def _validate_input(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload.get("user_id"), str) or not payload["user_id"].strip():
        raise ValueError("Missing or invalid field: user_id")

    target = payload.get("target")
    if not isinstance(target, dict):
        raise ValueError("Missing or invalid field: target")
    if not isinstance(target.get("area_id"), str) or not target["area_id"].strip():
        raise ValueError("Missing or invalid field: target.area_id")
    if not isinstance(target.get("job_id"), int):
        raise ValueError("Missing or invalid field: target.job_id")

    skills = payload.get("skills")
    if not isinstance(skills, list) or len(skills) == 0:
        raise ValueError("Missing or invalid field: skills (must be a non-empty array)")

    seen: set[int] = set()
    for s in skills:
        if not isinstance(s, dict):
            raise ValueError("Invalid skills entry: must be object")
        if not isinstance(s.get("skill_id"), int):
            raise ValueError("Invalid skills entry: missing skill_id")
        if s["skill_id"] in seen:
            raise ValueError(f"Invalid skills entry: duplicated skill_id={s['skill_id']}")
        seen.add(s["skill_id"])
        ul = s.get("user_level")
        if not isinstance(ul, int) or ul < 0 or ul > 10:
            raise ValueError(f"Invalid user_level for skill_id={s['skill_id']}: must be int 0-10")


def run_gap_analysis(
    payload: Mapping[str, Any],
    *,
    catalog: Optional[Catalog] = None,
    consent_level: Optional[int] = None,
) -> Dict[str, Any]:
    _validate_input(payload)
    if catalog is None:
        catalog = Catalog()

    user_id = str(payload["user_id"])
    if consent_level is None:
        consent_level = payload.get("consent_level")
    if consent_level not in (1, 2):
        raise ValueError("Missing or invalid consent_level (must be 1 or 2)")
    consent_level = int(consent_level)
    area_id = str(payload["target"]["area_id"])
    job_id = int(payload["target"]["job_id"])

    job = catalog.get_job(job_id)
    if job["area_id"] != area_id:
        raise ValueError(f"Target mismatch: job_id={job_id} does not belong to area_id={area_id}")

    requirements = catalog.get_requirements(job_id)
    if not requirements:
        raise ValueError(f"No requirements found for job_id={job_id}")

    user_levels_0_10: Dict[int, int] = {int(s["skill_id"]): int(s["user_level"]) for s in payload["skills"]}

    skills_analysis: List[Dict[str, Any]] = []
    penalty_details: List[Dict[str, Any]] = []

    coverage_score = 0.0
    gap_overall = 0.0
    penalty_sum = 0.0
    skills_covered = 0
    skills_partial = 0
    skills_missing = 0
    critical_under_threshold = 0

    category_acc: Dict[str, Dict[str, float]] = {c: {"w_sum": 0.0, "uw_sum": 0.0, "wgap_sum": 0.0} for c in CANONICAL_CATEGORIES}
    category_counts: Dict[str, Dict[str, int]] = {c: {"covered": 0, "partial": 0, "missing": 0} for c in CANONICAL_CATEGORIES}

    for req in requirements:
        user_level = user_levels_0_10.get(req.skill_id, 0)
        u_norm = user_level / 10.0
        gap = max(0.0, req.expected_level - u_norm)
        priority_score = req.weight * gap

        coverage_score += u_norm * req.weight
        gap_overall += req.weight * gap

        if u_norm >= req.expected_level:
            status = "coperta"
            skills_covered += 1
            if req.category in category_counts:
                category_counts[req.category]["covered"] += 1
        elif u_norm > 0.0:
            status = "parziale"
            skills_partial += 1
            if req.category in category_counts:
                category_counts[req.category]["partial"] += 1
        else:
            status = "mancante"
            skills_missing += 1
            if req.category in category_counts:
                category_counts[req.category]["missing"] += 1

        under_threshold = bool(req.is_critical and u_norm < req.threshold)
        if under_threshold:
            critical_under_threshold += 1
            penalty_sum += req.penalty
            skill_meta = catalog.get_skill(req.skill_id)
            penalty_details.append(
                {
                    "skill_id": req.skill_id,
                    "skill_name": skill_meta["skill_name"],
                    "threshold": _round(req.threshold, 2),
                    "user_level_normalized": _round(u_norm, 2),
                    "penalty": _round(req.penalty, 2),
                }
            )

        if req.category in category_acc:
            category_acc[req.category]["w_sum"] += req.weight
            category_acc[req.category]["uw_sum"] += u_norm * req.weight
            category_acc[req.category]["wgap_sum"] += req.weight * gap

        skill_meta = catalog.get_skill(req.skill_id)
        skills_analysis.append(
            {
                "skill_id": req.skill_id,
                "skill_name": skill_meta["skill_name"],
                "category": req.category,
                "weight": _round(req.weight, 3),
                "expected_level": _round(req.expected_level, 2),
                "user_level": user_level,
                "user_level_normalized": _round(u_norm, 2),
                "gap": _round(gap, 2),
                "priority_score": _round(priority_score, 4),
                "status": status,
                "is_critical": bool(req.is_critical),
                "threshold": _round(req.threshold, 2),
                "under_threshold": under_threshold,
            }
        )

    penalty_applied = penalty_sum > 0.0
    score_final = max(0.0, coverage_score - penalty_sum)
    position_index = score_final

    skills_analysis.sort(key=lambda x: (x["priority_score"], x["gap"]), reverse=True)

    category_metrics: Dict[str, Any] = {}
    for cat in CANONICAL_CATEGORIES:
        w_sum = category_acc[cat]["w_sum"]
        if w_sum <= 0.0:
            score_c = 0.0
            gap_c = 0.0
        else:
            score_c = category_acc[cat]["uw_sum"] / w_sum
            gap_c = category_acc[cat]["wgap_sum"] / w_sum

        category_metrics[cat] = {
            "score": _round(score_c, 2),
            "gap": _round(gap_c, 2),
            "status": _category_status(score_c),
            "weight_incidence": _round(w_sum, 2),
            "skills_covered": category_counts[cat]["covered"],
            "skills_partial": category_counts[cat]["partial"],
            "skills_missing": category_counts[cat]["missing"],
        }

    training_priorities: List[Dict[str, Any]] = []
    for s in skills_analysis:
        if s["gap"] <= 0:
            continue
        training_priorities.append(
            {
                "skill_id": s["skill_id"],
                "skill_name": s["skill_name"],
                "category": s["category"],
                "priority_score": s["priority_score"],
                "gap": s["gap"],
                "current_level": s["user_level"],
                "expected_level_label": _expected_level_label(float(s["expected_level"])),
            }
        )
        if len(training_priorities) >= 5:
            break

    out: Dict[str, Any] = {
        "analysis": {"id": _analysis_id(user_id), "timestamp": _iso_now(), "consent_level": consent_level},
        "user": {"user_id": user_id},
        "target_role": {
            "area_id": area_id,
            "area_name": catalog.get_area_name(area_id),
            "job_id": job_id,
            "job_title": job["job_title"],
            "total_skills_required": len(requirements),
        },
        "overall_metrics": {
            "coverage_score": _round(coverage_score, 2),
            "penalty_applied": bool(penalty_applied),
            "penalty_details": penalty_details,
            "score_final": _round(score_final, 2),
            "gap_overall": _round(gap_overall, 2),
            "position_index": _round(position_index, 2),
            "compatibility": _compatibility_label(score_final),
            "skills_covered": skills_covered,
            "skills_partial": skills_partial,
            "skills_missing": skills_missing,
            "critical_skills_under_threshold": critical_under_threshold,
        },
        "category_metrics": category_metrics,
        "skills_analysis": skills_analysis,
        "training_priorities": training_priorities,
    }

    return out


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SkillBridge scoring engine (Gap Analysis).")
    parser.add_argument("--input", required=True, help="Path to JSON input payload")
    parser.add_argument("--output", help="Optional path to write JSON output. Defaults to stdout.")
    parser.add_argument(
        "--consent-level",
        type=int,
        choices=[1, 2],
        help="Server-derived consent level (preferred). If omitted, tries to read consent_level from input JSON.",
    )
    args = parser.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    result = run_gap_analysis(payload, consent_level=args.consent_level)
    out_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
            f.write("\n")
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
