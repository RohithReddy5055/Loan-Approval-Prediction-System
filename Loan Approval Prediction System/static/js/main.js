/**
 * Main JavaScript for Loan Approval Prediction System
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loanForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous results and errors
        resultsSection.style.display = 'none';
        errorAlert.style.display = 'none';
        
        // Validate form
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        // Collect form data
        const formData = {
            Gender: document.getElementById('Gender').value,
            Married: document.getElementById('Married').value,
            Dependents: document.getElementById('Dependents').value,
            Education: document.getElementById('Education').value,
            Self_Employed: document.getElementById('Self_Employed').value,
            ApplicantIncome: parseFloat(document.getElementById('ApplicantIncome').value),
            CoapplicantIncome: parseFloat(document.getElementById('CoapplicantIncome').value),
            LoanAmount: parseFloat(document.getElementById('LoanAmount').value),
            Loan_Amount_Term: parseFloat(document.getElementById('Loan_Amount_Term').value),
            Credit_History: parseFloat(document.getElementById('Credit_History').value),
            Property_Area: document.getElementById('Property_Area').value
        };
        
        try {
            // Make API call
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Prediction failed');
            }
            
            // Display results
            displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while processing your request');
        } finally {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-search me-2"></i>Predict Loan Approval';
        }
    });
    
    /**
     * Display prediction results
     */
    function displayResults(data) {
        const resultCard = document.getElementById('resultCard');
        const resultTitle = document.getElementById('resultTitle');
        const resultIcon = document.getElementById('resultIcon');
        const probabilityBar = document.getElementById('probabilityBar');
        const probabilityText = document.getElementById('probabilityText');
        const featureImportance = document.getElementById('featureImportance');
        
        // Set result title and icon
        if (data.status === 'approved') {
            resultTitle.textContent = 'Loan Approved!';
            resultIcon.className = 'fas fa-check-circle me-2 text-success';
            resultCard.className = 'card border-success';
            probabilityBar.className = 'progress-bar approved';
        } else {
            resultTitle.textContent = 'Loan Rejected';
            resultIcon.className = 'fas fa-times-circle me-2 text-danger';
            resultCard.className = 'card border-danger';
            probabilityBar.className = 'progress-bar rejected';
        }
        
        // Set probability
        const probability = data.probability || 0;
        probabilityBar.style.width = probability + '%';
        probabilityBar.setAttribute('aria-valuenow', probability);
        probabilityText.textContent = probability.toFixed(2) + '%';
        
        // Display feature importance
        if (data.feature_importance && Object.keys(data.feature_importance).length > 0) {
            let importanceHTML = '<h6 class="mt-3 mb-2"><i class="fas fa-info-circle me-2"></i>Key Factors:</h6><div class="list-group">';
            
            Object.entries(data.feature_importance).forEach(([feature, importance]) => {
                const importancePercent = (importance * 100).toFixed(2);
                importanceHTML += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <span><strong>${formatFeatureName(feature)}</strong></span>
                            <span class="badge bg-primary">${importancePercent}%</span>
                        </div>
                    </div>
                `;
            });
            
            importanceHTML += '</div>';
            featureImportance.innerHTML = importanceHTML;
        } else {
            featureImportance.innerHTML = '';
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    /**
     * Format feature name for display
     */
    function formatFeatureName(name) {
        return name
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });

});

