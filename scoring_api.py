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
    def score_criterion(criterion, data):
        # Base case: leaf node
        if not criterion.children:
            score = random.uniform(3.0, 5.0)  # Mock scoring for demo
            return {
                'score': score,
                'name': criterion.name,
                'explanation': generate_subscore_explanation(criterion.content, score)
            }
        
        # Recursive case: internal node
        child_results = [score_criterion(child, data) for child in criterion.children]
        total_weight = sum(child.weight for child in criterion.children)
        weighted_sum = sum(result['score'] * child.weight / total_weight 
                         for result, child in zip(child_results, criterion.children))
        
        return {
            'score': weighted_sum,
            'name': criterion.name,
            'children': child_results
        }
    
    # Score the entire criterion tree
    result = score_criterion(criteria.root_criterion, resume_data)
    
    # Format for API response
    category_scores = {
        child['name']: child['score']
        for child in result.get('children', [])
    }
    
    explanations = {
        child['name']: {
            k: v for k, v in child.items() if k != 'name'
        }
        for child in result.get('children', [])
    }
    
    return {
        'final_score': result['score'],
        'category_scores': category_scores,
        'explanations': explanations
    }
