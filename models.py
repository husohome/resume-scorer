from typing import Dict, List, Optional, Union, Tuple, Annotated
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class Criterion(BaseModel):
    name: str
    content: str
    scale: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    children: List[Tuple[float, "Criterion"]] = Field(default_factory=list)

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Weight must be between 0 and 1")
        return v

    @field_validator("children")
    @classmethod
    def validate_children(cls, v: List[Tuple[float, "Criterion"]]) -> List[Tuple[float, "Criterion"]]:
        total_weight = sum(weight for weight, _ in v)
        if total_weight > 0 and abs(total_weight - 1.0) > 0.001:  # Allow small floating point differences
            raise ValueError("Child weights must sum to 1.0")
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
        scores = {}
        weighted_sum = 0.0
        
        for weight, child in self.children:
            child_score, child_details = child.calculate_score(data)
            weighted_score = child_score * weight  # No need to normalize, weights should sum to 1
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

    @field_validator('weights')
    @classmethod
    def validate_weights(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if v is not None:
            if not all(0 <= w <= 1 for w in v.values()):
                raise ValueError('All weights must be between 0 and 1')
        return v

# Update the Criterion model reference for self-referential type
Criterion.model_rebuild()
