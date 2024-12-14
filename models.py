from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

class Criterion(BaseModel):
    name: str
    content: str
    scale: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    children: Optional[List['Criterion']] = Field(default_factory=list)

    @validator('weight')
    def validate_weight(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Weight must be between 0 and 1')
        return v

    def calculate_score(self, data: dict) -> tuple[float, dict]:
        """Calculate score for this criterion and its children"""
        if not self.children:
            # Leaf node - generate score based on content
            score = data.get(self.content, 0.0)
            return score, {
                "score": score,
                "explanation": f"Evaluated {self.content} using {self.scale}"
            }
        
        # Non-leaf node - aggregate children scores
        total_weight = sum(child.weight for child in self.children)
        scores = {}
        weighted_sum = 0.0
        
        for child in self.children:
            child_score, child_details = child.calculate_score(data)
            weighted_score = (child_score * child.weight) / total_weight
            weighted_sum += weighted_score
            scores[child.name] = child_details
        
        return weighted_sum, {
            "score": weighted_sum,
            "children": scores
        }

class Resume(BaseModel):
    id: str
    filename: str
    personal: dict
    non_personal: dict
    uploaded_at: datetime = Field(default_factory=datetime.now)

class ScoringResult(BaseModel):
    final_score: float
    category_scores: Dict[str, float]
    explanations: Dict[str, Dict[str, Union[float, str, dict]]]

class ScoringRequest(BaseModel):
    resume_id: str
    criteria_id: str
    weights: Optional[Dict[str, float]] = None

    @validator('weights')
    def validate_weights(cls, v):
        if v is not None:
            if not all(0 <= w <= 1 for w in v.values()):
                raise ValueError('All weights must be between 0 and 1')
        return v

# Update the Criterion model reference for self-referential type
Criterion.model_rebuild()
