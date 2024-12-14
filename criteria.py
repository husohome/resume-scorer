PRESET_CRITERIA = {
    "default": {
        "name": "Standard Technical Evaluation",
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
        },
        "weights": {
            "technical_skills": 0.40,
            "experience": 0.35,
            "education": 0.25
        }
    },
    "senior_dev": {
        "name": "Senior Developer Focus",
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
        },
        "weights": {
            "technical_skills": 0.50,
            "experience": 0.40,
            "education": 0.10
        }
    }
}

def get_preset_criteria():
    return PRESET_CRITERIA
