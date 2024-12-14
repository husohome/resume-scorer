document.addEventListener('DOMContentLoaded', function() {
    const scoreButton = document.getElementById('scoreButton');
    const criteriaSelect = document.getElementById('criteriaSelect');
    const resultsDiv = document.getElementById('scoringResults');
    
    scoreButton.addEventListener('click', async function() {
        const resumeId = window.location.pathname.split('/').pop();
        const criteriaId = criteriaSelect.value;
        
        try {
            const response = await fetch('/api/score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resume_id: resumeId,
                    criteria_id: criteriaId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayResults(data);
            } else {
                resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        } catch (error) {
            resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        }
    });
    
    async function calculateScore() {
        const criteriaId = criteriaSelect.value;
        const resumeId = window.location.pathname.split('/').pop();
        
        try {
            const response = await fetch('/api/score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resume_id: resumeId,
                    criteria_id: criteriaId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            displayResults(data);
        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h4>Error calculating score</h4>
                    <p>There was an error processing your request. Please try again.</p>
                    <p class="text-muted">Technical details: ${error.message}</p>
                </div>
            `;
            console.error('Scoring error:', error);
        }
    }

    function displayResults(data) {
        function getScoreColorClass(score) {
            if (score >= 4.5) return 'bg-success';
            if (score >= 3.5) return 'bg-info';
            if (score >= 2.5) return 'bg-warning';
            return 'bg-danger';
        }

        let html = `
            <div class="alert alert-primary">
                <h4 class="mb-3">Final Score: ${(data.final_score || 0).toFixed(2)}/5.0</h4>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar ${getScoreColorClass(data.final_score || 0)}" 
                         role="progressbar" 
                         style="width: ${((data.final_score || 0)/5)*100}%">
                        ${(data.final_score || 0).toFixed(2)}
                    </div>
                </div>
            </div>
            <div class="accordion" id="scoreAccordion">
        `;
        
        for (const [category, scores] of Object.entries(data.category_scores)) {
            const categoryScore = scores;
            const explanations = data.explanations[category];
            
            const categoryId = category.toLowerCase().replace(/[^a-z0-9]/g, '');
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#collapse${categoryId}">
                            ${category.replace(/_/g, ' ').toUpperCase()} - Score: ${(categoryScore || 0).toFixed(2)}
                        </button>
                    </h2>
                    <div id="collapse${categoryId}" class="accordion-collapse collapse">
                        <div class="accordion-body">
                            <ul class="list-group">
            `;
            
            function renderCriteriaDetails(details, level = 0) {
                let html = '';
                const score = details.score || 0;
                const padding = level * 20; // Indent nested criteria
                
                html += `
                    <li class="list-group-item" style="padding-left: ${padding}px">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${details.name || 'Score'}:</strong> ${score.toFixed(2)}/5
                                ${details.explanation ? `<br><small class="text-muted">${details.explanation}</small>` : ''}
                            </div>
                            <div class="progress" style="width: 100px;">
                                <div class="progress-bar ${getScoreColorClass(score)}" 
                                     role="progressbar" 
                                     style="width: ${(score/5)*100}%">
                                </div>
                            </div>
                        </div>
                    </li>
                `;
                
                if (details.children) {
                    for (const [childName, childDetails] of Object.entries(details.children)) {
                        html += renderCriteriaDetails({...childDetails, name: childName}, level + 1);
                    }
                }
                
                return html;
            }
            
            html += renderCriteriaDetails(explanations);
            
            html += `
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        resultsDiv.innerHTML = html;
    }
});
