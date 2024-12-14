MOCK_RESUMES = {
    "1": {
        "id": "1",
        "filename": "john_doe_resume.pdf",
        "personal": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-0123"
        },
        "non_personal": {
            "technical_skills": {
                "programming": ["Python", "JavaScript", "Java"],
                "frameworks": ["Django", "React", "Spring"],
                "tools": ["Git", "Docker", "AWS"]
            },
            "experience": {
                "work_history": [
                    {
                        "title": "Senior Developer",
                        "duration": "3 years",
                        "achievements": ["Led team of 5", "Improved performance by 40%"]
                    }
                ],
                "projects": [
                    {
                        "name": "E-commerce Platform",
                        "technologies": ["Python", "Django", "React"]
                    }
                ]
            },
            "education": {
                "degree": "Master's in Computer Science",
                "courses": ["Machine Learning", "Software Engineering", "Algorithms"]
            }
        }
    },
    "2": {
        "id": "2",
        "filename": "jane_smith_resume.pdf",
        "personal": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "555-0124"
        },
        "non_personal": {
            "technical_skills": {
                "programming": ["Python", "C++", "Ruby"],
                "frameworks": ["Flask", "Rails", "Qt"],
                "tools": ["Git", "Jenkins", "Kubernetes"]
            },
            "experience": {
                "work_history": [
                    {
                        "title": "Software Engineer",
                        "duration": "2 years",
                        "achievements": ["Developed CI/CD pipeline", "Reduced bugs by 30%"]
                    }
                ],
                "projects": [
                    {
                        "name": "Data Analytics Dashboard",
                        "technologies": ["Python", "Flask", "D3.js"]
                    }
                ]
            },
            "education": {
                "degree": "Bachelor's in Software Engineering",
                "courses": ["Data Structures", "Web Development", "Database Systems"]
            }
        }
    }
}

def get_mock_resumes():
    return MOCK_RESUMES

def get_resume_by_id(resume_id):
    return MOCK_RESUMES.get(str(resume_id))
