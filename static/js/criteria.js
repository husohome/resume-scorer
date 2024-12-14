document.addEventListener('DOMContentLoaded', function() {
    const criteriaSelect = document.getElementById('criteriaSelect');
    const weightInputs = document.querySelectorAll('[data-weight-input]');
    
    criteriaSelect.addEventListener('change', function() {
        const selectedCriteria = this.value;
        updateWeightInputs(selectedCriteria);
    });
    
    function updateWeightInputs(criteriaId) {
        weightInputs.forEach(input => {
            const category = input.dataset.category;
            const weight = criteria[criteriaId].weights[category];
            input.value = weight;
        });
    }
    
    // Initialize with default criteria
    if (criteriaSelect) {
        updateWeightInputs(criteriaSelect.value);
    }
});
