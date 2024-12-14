import random
import logging

def generate_subscore_explanation(category, score):
    explanations = {
        "programming_skills": f"Programming skills rated at {score:.1f}/5 based on language diversity and relevance",
        "framework_expertise": f"Framework knowledge scored {score:.1f}/5 considering modern technology stack",
        "tool_proficiency": f"Development tools proficiency at {score:.1f}/5",
        "employment_history": f"Work experience rated {score:.1f}/5 based on roles and achievements",
        "project_portfolio": f"Project portfolio scored {score:.1f}/5 for complexity and impact",
        "degree_relevance": f"Educational qualification rated {score:.1f}/5",
        "course_relevance": f"Relevant coursework scored {score:.1f}/5"
    }
    return explanations.get(category, f"Scored {score:.1f}/5")

def score_resume(resume_data, criteria):
    def score_criterion(criterion, data):
        logging.debug(f"Scoring criterion: {criterion.get('name', 'Unknown')}")
        
        # Base case: if no children or empty children list
        children = criterion.get('children', [])
        if not children:
            # Mock scoring logic - replace with actual scoring logic in production
            content = criterion.get('content', '')
            base_score = random.uniform(3.0, 5.0)  # Mock scoring for demo
            return {
                'score': float(base_score),
                'explanation': generate_subscore_explanation(content, base_score)
            }
        
        # Recursive case: internal node with children
        child_results = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        # Handle both list and dict formats
        for child_entry in children:
            # Handle array format [weight, criterion]
            if isinstance(child_entry, (list, tuple)):
                weight = float(child_entry[0])
                child = child_entry[1]
            # Handle dictionary format with weight property
            else:
                weight = float(child_entry.get('weight', 1.0))
                child = child_entry
            
            child_result = score_criterion(child, data)
            child_name = child.get('name', 'Unknown')
            
            weighted_sum += child_result['score'] * weight
            total_weight += weight
            
            # Store child result with weight information
            child_results[child_name] = {
                **child_result,
                'weight': weight
            }
        
        # Normalize the score if weights don't sum to 1
        final_score = weighted_sum / total_weight if total_weight > 0 else weighted_sum
        
        return {
            'score': float(final_score),
            'children': child_results,
            'explanation': f"Aggregated score based on {len(children)} subcriteria"
        }
    
    try:
        logging.debug("Starting resume scoring process")
        # Score the entire criterion tree
        result = score_criterion(criteria, resume_data)
        
        # Format for API response
        category_scores = {}
        explanations = {}
        
        # Process top-level categories
        if 'children' in result:
            for category, details in result['children'].items():
                category_scores[category] = details['score']
                explanations[category] = {
                    'score': details['score'],
                    'explanation': details.get('explanation', ''),
                }
                if 'children' in details:
                    explanations[category]['children'] = details['children']
        
        response_data = {
            'final_score': float(result['score']),
            'category_scores': {k: float(v) for k, v in category_scores.items()},
            'explanations': explanations
        }
        
        logging.debug(f"Scoring complete. Final score: {response_data['final_score']}")
        return response_data
        
    except Exception as e:
        logging.error(f"Error in score_resume: {str(e)}")
        raise
