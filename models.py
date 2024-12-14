from typing import List, Optional
from pydantic import BaseModel, Field

class Criterion(BaseModel):
    name: str
    content: str
    scale: str
    children: Optional[List['Criterion']] = Field(default_factory=list)

class Resume(BaseModel):
    id: str
    filename: str
    personal: dict
    non_personal: dict

class ScoringResult(BaseModel):
    final_score: float
    category_scores: dict
    explanations: dict

class ScoringRequest(BaseModel):
    resume_id: str
    criteria_id: str
    weights: Optional[dict] = None

# Update the Criterion model reference for self-referential type
Criterion.model_rebuild()
