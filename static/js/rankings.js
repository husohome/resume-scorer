document.addEventListener('DOMContentLoaded', function() {
    const criteriaSelect = document.getElementById('criteriaSelect');
    const updateButton = document.getElementById('updateRankings');
    const rankingsContainer = document.getElementById('rankingsContainer');

    async function updateRankings() {
        const criteriaId = criteriaSelect.value;
        
        try {
            const response = await fetch('/api/rank', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    criteria_id: criteriaId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const rankings = await response.json();
            displayRankings(rankings);
        } catch (error) {
            console.error('Error updating rankings:', error);
            rankingsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h4>Error updating rankings</h4>
                    <p>There was an error processing your request. Please try again.</p>
                    <p class="text-muted">Technical details: ${error.message}</p>
                </div>
            `;
        }
    }

    function displayRankings(rankings) {
        rankingsContainer.innerHTML = rankings.map(resume => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h5 class="card-title">${resume.filename}</h5>
                            <div class="mb-2">
                                <strong>Score: </strong>
                                <span class="badge bg-primary">${resume.score.toFixed(2)}/5.0</span>
                            </div>
                            <div class="mb-2">
                                <strong>Technical Skills:</strong>
                                <ul class="list-inline">
                                    ${resume.non_personal.technical_skills.programming
                                        .slice(0, 3)
                                        .map(skill => `
                                            <li class="list-inline-item badge bg-secondary">${skill}</li>
                                        `).join('')}
                                </ul>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <a href="/scoring/${resume.id}" class="btn btn-outline-primary">View Details</a>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Update rankings when criteria changes
    criteriaSelect.addEventListener('change', updateRankings);
    
    // Initial load of rankings
    updateRankings();
});
