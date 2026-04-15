from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from auth_schema import Target


class SkillInput(BaseModel):
    skill_id: int = Field(...)
    user_level: int = Field(..., ge=0, le=10)


class UserSkillInput(BaseModel):
    timestamp: datetime
    user_id: str
    target: Target
    skills: List[SkillInput]
