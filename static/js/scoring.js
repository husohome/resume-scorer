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
    
    function displayResults(data) {
    function getScoreColorClass(score) {
        if (score >= 4.5) return 'bg-success';
        if (score >= 3.5) return 'bg-info';
        if (score >= 2.5) return 'bg-warning';
        return 'bg-danger';
    }

        let html = `
            <div class="alert alert-primary">
                <h4 class="mb-3">Final Score: ${data.final_score.toFixed(2)}/5.0</h4>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar ${getScoreColorClass(data.final_score)}" 
                         role="progressbar" 
                         style="width: ${(data.final_score/5)*100}%">
                        ${data.final_score.toFixed(2)}
                    </div>
                </div>
            </div>
            <div class="accordion" id="scoreAccordion">
        `;
        
        for (const [category, scores] of Object.entries(data.category_scores)) {
            const categoryScore = scores;
            const explanations = data.explanations[category];
            
            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#collapse${category}">
                            ${category.replace('_', ' ').toUpperCase()} - Score: ${categoryScore.toFixed(2)}
                        </button>
                    </h2>
                    <div id="collapse${category}" class="accordion-collapse collapse">
                        <div class="accordion-body">
                            <ul class="list-group">
            `;
            
            for (const [subcategory, details] of Object.entries(explanations)) {
                html += `
                    <li class="list-group-item">
                        <strong>${subcategory}:</strong> ${details.score.toFixed(2)}/5
                        <br>
                        <small class="text-muted">${details.explanation}</small>
                    </li>
                `;
            }
            
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
