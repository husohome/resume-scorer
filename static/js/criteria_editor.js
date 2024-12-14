document.addEventListener('DOMContentLoaded', function() {
    const criteriaForm = document.getElementById('criteriaForm');
    const criteriaEditor = document.getElementById('criteriaEditor');
    const criteriaList = document.getElementById('criteriaList');
    
    function createCriterionNode(criterion, level = 0) {
        const node = document.createElement('div');
        node.className = 'criterion-node mb-3';
        node.style.marginLeft = `${level * 20}px`;
        
        const content = `
            <div class="card">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label">Name</label>
                            <input type="text" class="form-control" 
                                   placeholder="Criterion Name" 
                                   value="${criterion.name || ''}"
                                   data-field="name">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Content to Evaluate</label>
                            <input type="text" class="form-control" 
                                   placeholder="What does this criterion evaluate?" 
                                   value="${criterion.content || ''}"
                                   data-field="content">
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">Weight</label>
                            <input type="number" class="form-control" 
                                   placeholder="Weight" 
                                   min="0" max="1" step="0.1"
                                   value="${criterion.weight || 1.0}"
                                   data-field="weight">
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">&nbsp;</label>
                            <div>
                                <button class="btn btn-outline-primary btn-sm me-2 add-child">
                                    Add Child
                                </button>
                                <button class="btn btn-outline-danger btn-sm remove-node">
                                    Remove
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="children mt-3"></div>
                </div>
            </div>
        `;
        
        node.innerHTML = content;
        
        // Add child nodes if they exist
        const childrenContainer = node.querySelector('.children');
        if (criterion.children) {
            criterion.children.forEach(([weight, childCriterion]) => {
                childCriterion.weight = weight;
                const childNode = createCriterionNode(childCriterion, level + 1);
                childrenContainer.appendChild(childNode);
            });
        }
        
        // Setup event listeners
        node.querySelector('.add-child').addEventListener('click', () => {
            const childNode = createCriterionNode({
                name: 'New Criterion',
                weight: 1.0,
                content: '',
                scale: '',
                children: []
            }, level + 1);
            childrenContainer.appendChild(childNode);
            normalizeWeights(childrenContainer);
        });
        
        node.querySelector('.remove-node').addEventListener('click', () => {
            const parent = node.parentElement;
            node.remove();
            if (parent) {
                normalizeWeights(parent);
            }
        });
        
        node.querySelector('[data-field="weight"]').addEventListener('change', (e) => {
            normalizeWeights(node.parentElement);
        });
        
        return node;
    }
    
    function normalizeWeights(container) {
        if (!container) return;
        
        const nodes = container.children;
        if (nodes.length === 0) return;
        
        let totalWeight = 0;
        const weights = [];
        
        // Calculate total weight
        for (const node of nodes) {
            const weightInput = node.querySelector('[data-field="weight"]');
            const weight = parseFloat(weightInput.value) || 0;
            weights.push(weight);
            totalWeight += weight;
        }
        
        // Normalize weights
        if (totalWeight > 0) {
            for (let i = 0; i < nodes.length; i++) {
                const weightInput = nodes[i].querySelector('[data-field="weight"]');
                const normalizedWeight = weights[i] / totalWeight;
                weightInput.value = normalizedWeight.toFixed(2);
            }
        }
    }
    
    function serializeCriterion(node) {
        const criterion = {
            name: node.querySelector('[data-field="name"]').value,
            content: node.querySelector('[data-field="content"]').value,
            scale: "1-5 scale",
            children: []
        };
        
        const childrenContainer = node.querySelector('.children');
        const childNodes = childrenContainer.children;
        
        for (const childNode of childNodes) {
            const weight = parseFloat(childNode.querySelector('[data-field="weight"]').value);
            const childCriterion = serializeCriterion(childNode);
            criterion.children.push([weight, childCriterion]);
        }
        
        return criterion;
    }
    
    criteriaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('criteriaName').value;
        
        const rootCriterion = {
            name: `Total score of ${name}`,
            content: 'overall_evaluation',
            scale: '1-5 scale',
            children: []
        };
        
        criteriaEditor.innerHTML = '';
        const rootNode = createCriterionNode(rootCriterion);
        criteriaEditor.appendChild(rootNode);

        // Add save button after creating the root node
        const saveButton = document.createElement('button');
        saveButton.className = 'btn btn-success mt-3';
        saveButton.textContent = 'Save Criteria';
        saveButton.addEventListener('click', async () => {
            const criteriaData = {
                name: name,
                root_criterion: serializeCriterion(rootNode)
            };
            
            try {
                const response = await fetch('/api/criteria', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(criteriaData)
                });
                
                if (!response.ok) {
                    throw new Error('Failed to save criteria');
                }
                
                const result = await response.json();
                alert('Criteria saved successfully!');
                location.reload(); // Refresh to show new criteria
            } catch (error) {
                console.error('Error saving criteria:', error);
                alert('Failed to save criteria: ' + error.message);
            }
        });
        
        criteriaEditor.appendChild(saveButton);
    });
    
    criteriaList.addEventListener('click', async (e) => {
        e.preventDefault();
        const criteriaId = e.target.closest('[data-criteria-id]')?.dataset.criteriaId;
        if (!criteriaId) return;
        
        try {
            const response = await fetch(`/api/criteria/${criteriaId}`);
            if (!response.ok) throw new Error('Failed to fetch criteria');
            
            const data = await response.json();
            criteriaEditor.innerHTML = '';
            const rootNode = createCriterionNode(data.root_criterion);
            criteriaEditor.appendChild(rootNode);
        } catch (error) {
            console.error('Error loading criteria:', error);
            criteriaEditor.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load criteria: ${error.message}
                </div>
            `;
        }
    });
});
