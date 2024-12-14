from typing import Dict
from models import Criterion

def create_technical_criterion(weight_config: dict) -> Criterion:
    return Criterion(
        name="Technical Skills",
        content="technical_evaluation",
        scale="Skills proficiency scale (1-5)",
        weight=weight_config["weights"]["technical_skills"],
        children=[
            Criterion(
                name="Programming Languages",
                content="programming_skills",
                scale="Language proficiency and diversity",
                weight=weight_config["structure"]["technical_skills"]["programming"]["weight"]
            ),
            Criterion(
                name="Frameworks & Libraries",
                content="framework_knowledge",
                scale="Framework expertise level",
                weight=weight_config["structure"]["technical_skills"]["frameworks"]["weight"]
            ),
            Criterion(
                name="Development Tools",
                content="tool_proficiency",
                scale="Tool usage and familiarity",
                weight=weight_config["structure"]["technical_skills"]["tools"]["weight"]
            )
        ]
    )

def create_experience_criterion(weight_config: dict) -> Criterion:
    return Criterion(
        name="Professional Experience",
        content="experience_evaluation",
        scale="Experience depth and relevance",
        weight=weight_config["weights"]["experience"],
        children=[
            Criterion(
                name="Work History",
                content="work_history_analysis",
                scale="Role relevance and impact",
                weight=weight_config["structure"]["experience"]["work_history"]["weight"]
            ),
            Criterion(
                name="Projects",
                content="project_evaluation",
                scale="Project complexity and achievements",
                weight=weight_config["structure"]["experience"]["projects"]["weight"]
            )
        ]
    )

def create_education_criterion(weight_config: dict) -> Criterion:
    return Criterion(
        name="Education",
        content="education_evaluation",
        scale="Educational qualification relevance",
        weight=weight_config["weights"]["education"],
        children=[
            Criterion(
                name="Degree",
                content="degree_relevance",
                scale="Degree level and field relevance",
                weight=weight_config["structure"]["education"]["degree"]["weight"]
            ),
            Criterion(
                name="Courses",
                content="course_relevance",
                scale="Course relevance to position",
                weight=weight_config["structure"]["education"]["courses"]["weight"]
            )
        ]
    )

PRESET_CRITERIA: Dict[str, Dict] = {
    "default": {
        "name": "Standard Technical Evaluation",
        "weights": {
            "technical_skills": 0.40,
            "experience": 0.35,
            "education": 0.25
        },
        "structure": {
            "technical_skills": {
                "programming": {"weight": 0.15},
                "frameworks": {"weight": 0.15},
                "tools": {"weight": 0.10}
            },
            "experience": {
                "work_history": {"weight": 0.20},
                "projects": {"weight": 0.15}
            },
            "education": {
                "degree": {"weight": 0.15},
                "courses": {"weight": 0.10}
            }
        }
    },
    "senior_dev": {
        "name": "Senior Developer Focus",
        "weights": {
            "technical_skills": 0.50,
            "experience": 0.40,
            "education": 0.10
        },
        "structure": {
            "technical_skills": {
                "programming": {"weight": 0.20},
                "frameworks": {"weight": 0.15},
                "tools": {"weight": 0.15}
            },
            "experience": {
                "work_history": {"weight": 0.25},
                "projects": {"weight": 0.15}
            },
            "education": {
                "degree": {"weight": 0.05},
                "courses": {"weight": 0.05}
            }
        }
    }
}

def get_preset_criteria():
    criteria_dict = {}
    for key, config in PRESET_CRITERIA.items():
        criteria_dict[key] = {
            "name": config["name"],
            "root_criterion": Criterion(
                name=config["name"],
                content="overall_evaluation",
                scale="Overall candidate evaluation",
                weight=1.0,
                children=[
                    create_technical_criterion(config),
                    create_experience_criterion(config),
                    create_education_criterion(config)
                ]
            )
        }
    return criteria_dict
