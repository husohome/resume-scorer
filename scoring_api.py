import random
import logging

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
            # Mock scoring logic - replace with actual scoring logic in production
            base_score = random.uniform(3.0, 5.0)  # Mock scoring for demo
            
            return {
                'score': base_score,
                'name': criterion.name,
                'weight': criterion.weight,
                'explanation': generate_subscore_explanation(criterion.content, base_score)
            }
        
        # Recursive case: internal node
        child_results = {}
        weighted_sum = 0.0
        
        # Score each child criterion
        for weight, child in criterion.children:
            child_result = score_criterion(child, data)
            child_results[child.name] = child_result
            weighted_sum += child_result['score'] * weight
            
            # Add weight information to child result
            child_results[child.name]['weight'] = weight
        
        return {
            'score': weighted_sum,
            'name': criterion.name,
            'weight': criterion.weight,
            'children': child_results,
            'explanation': f"Aggregated score based on {len(criterion.children)} subcriteria"
        }
    
    try:
        # Score the entire criterion tree
        result = score_criterion(criteria, resume_data)
        
        # Format for API response
        category_scores = {}
        explanations = {}
        
        for category, details in result.get('children', {}).items():
            category_scores[category] = details['score']
            explanations[category] = {
                'score': details['score']
            }
            if 'explanation' in details:
                explanations[category]['explanation'] = details['explanation']
            if 'children' in details:
                explanations[category]['children'] = details['children']
        
        return {
            'final_score': result['score'],
            'category_scores': category_scores,
            'explanations': explanations
        }
    except Exception as e:
        logging.error(f"Error in score_resume: {str(e)}")
        raise
