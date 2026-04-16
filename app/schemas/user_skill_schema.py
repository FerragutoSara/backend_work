from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class Target(BaseModel):
    area_id: str
    job_id: int

class SkillInput(BaseModel):
    skill_id: int = Field(...)
    user_level: int = Field(..., ge=0, le=10)

class UserSkillInput(BaseModel):
    timestamp: Optional[datetime] = None
    user_id: str
    target: Target
    consent_level: Optional[int] = Field(None, ge=1, le=2)
    skills: List[SkillInput]
