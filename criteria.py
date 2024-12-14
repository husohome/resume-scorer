from typing import Dict
from models import Criterion

def create_technical_criterion(weight_config: dict) -> dict:
    """Create technical skills criterion with proper weight handling"""
    weights = weight_config.get("weights", {})
    return {
        "name": "Technical Skills Assessment",
        "content": "technical_skills",
        "scale": "Skills proficiency scale (1-5)",
        "weight": weights.get("technical_skills", 0.4),
        "children": [
            {
                "name": "Programming Languages",
                "content": "programming_skills",
                "weight": 0.4,
                "scale": "Language proficiency and diversity"
            },
            {
                "name": "Frameworks & Libraries",
                "content": "framework_expertise",
                "weight": 0.35,
                "scale": "Framework expertise level"
            },
            {
                "name": "Development Tools",
                "content": "tool_proficiency",
                "weight": 0.25,
                "scale": "Tool usage and familiarity"
            }
        ]
    }

def create_experience_criterion(weight_config: dict) -> dict:
    """Create experience criterion with proper weight handling"""
    weights = weight_config.get("weights", {})
    return {
        "name": "Professional Experience",
        "content": "work_experience",
        "scale": "Experience depth and relevance",
        "weight": weights.get("experience", 0.35),
        "children": [
            {
                "name": "Work History",
                "content": "employment_history",
                "weight": 0.6,
                "scale": "Role relevance and impact"
            },
            {
                "name": "Projects",
                "content": "project_portfolio",
                "weight": 0.4,
                "scale": "Project complexity and achievements"
            }
        ]
    }

def create_education_criterion(weight_config: dict) -> dict:
    """Create education criterion with proper weight handling"""
    weights = weight_config.get("weights", {})
    return {
        "name": "Education",
        "content": "educational_background",
        "scale": "Educational qualification relevance",
        "weight": weights.get("education", 0.25),
        "children": [
            {
                "name": "Degree",
                "content": "degree_relevance",
                "weight": 0.7,
                "scale": "Degree level and field relevance"
            },
            {
                "name": "Courses",
                "content": "course_relevance",
                "weight": 0.3,
                "scale": "Course relevance to position"
            }
        ]
    }

# Default weights for different evaluation focuses
DEFAULT_WEIGHTS = {
    "technical_skills": 0.4,
    "experience": 0.35,
    "education": 0.25
}

PRESET_CRITERIA: Dict[str, Dict] = {
    "default": {
        "name": "Standard Technical Evaluation",
        "weights": DEFAULT_WEIGHTS.copy()
    },
    "senior_dev": {
        "name": "Senior Developer Focus",
        "weights": {
            "technical_skills": 0.50,
            "experience": 0.40,
            "education": 0.10
        }
    }
}

def get_preset_criteria():
    """Get all preset criteria with proper weight handling."""
    criteria_dict = {}
    
    for key, config in PRESET_CRITERIA.items():
        # For custom criteria that already have a root_criterion defined
        if "root_criterion" in config:
            criteria_dict[key] = {
                "name": config["name"],
                "root_criterion": config["root_criterion"]
            }
            continue
            
        # Ensure weights dictionary exists with defaults
        weights = config.get("weights", DEFAULT_WEIGHTS.copy())
        
        # Create root criterion with proper structure
        root_criterion = {
            "name": f"Total score of {config['name']}",
            "content": "overall_evaluation",
            "scale": "Overall candidate evaluation",
            "weight": 1.0,
            "children": [
                create_technical_criterion({"weights": weights}),
                create_experience_criterion({"weights": weights}),
                create_education_criterion({"weights": weights})
            ]
        }
        
        criteria_dict[key] = {
            "name": config["name"],
            "root_criterion": root_criterion
        }
        
    return criteria_dict
