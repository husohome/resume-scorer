from typing import Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, field_validator
from database import db

class Criterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    scale = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    parent_id = db.Column(db.Integer, db.ForeignKey('criterion.id'))
    
    children = db.relationship(
        'Criterion',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            'name': self.name,
            'content': self.content,
            'scale': self.scale,
            'weight': self.weight,
            'children': [(c.weight, c.to_dict()) for c in self.children]
        }

    def calculate_score(self, data: dict) -> tuple[float, dict]:
        if not self.children.count():
            score = data.get(self.content, 0.0)
            return score, {
                "score": score,
                "explanation": f"Evaluated {self.content} using {self.scale}"
            }
        
        scores = {}
        weighted_sum = 0.0
        
        for child in self.children:
            child_score, child_details = child.calculate_score(data)
            weighted_score = child_score * child.weight
            weighted_sum += weighted_score
            scores[child.name] = child_details
        
        return weighted_sum, {
            "score": weighted_sum,
            "children": scores
        }

class Resume(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    personal = db.Column(db.JSON)
    non_personal = db.Column(db.JSON)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'personal': self.personal,
            'non_personal': self.non_personal,
            'uploaded_at': self.uploaded_at.isoformat()
        }

# Pydantic models for API request/response validation
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