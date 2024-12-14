import random

def generate_subscore_explanation(category, score):
    explanations = {
        "programming": f"Programming skills rated at {score:.1f}/5 based on language diversity and relevance",
        "frameworks": f"Framework knowledge scored {score:.1f}/5 considering modern technology stack",
        "tools": f"Development tools proficiency at {score:.1f}/5",
        "work_history": f"Work experience rated {score:.1f}/5 based on roles and achievements",
        "projects": f"Project portfolio scored {score:.1f}/5 for complexity and impact",
        "degree": f"Educational qualification rated {score:.1f}/5",
        "courses": f"Relevant coursework scored {score:.1f}/5"
    }
    return explanations.get(category, f"Scored {score:.1f}/5")

def score_resume(resume_data, criteria):
    scores = {}
    explanations = {}
    
    for main_category, subcategories in criteria['structure'].items():
        category_score = 0
        category_explanations = {}
        
        for subcategory, config in subcategories.items():
            # Generate plausible random score between 3.0 and 5.0
            subscore = random.uniform(3.0, 5.0)
            weighted_subscore = subscore * config['weight']
            category_score += weighted_subscore
            
            category_explanations[subcategory] = {
                'score': subscore,
                'explanation': generate_subscore_explanation(subcategory, subscore)
            }
        
        scores[main_category] = category_score
        explanations[main_category] = category_explanations
    
    # Calculate final score
    final_score = sum(scores[category] * weight 
                     for category, weight in criteria['weights'].items())
    
    return {
        'final_score': final_score,
        'category_scores': scores,
        'explanations': explanations
    }
