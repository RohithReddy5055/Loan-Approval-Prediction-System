/**
 * Car Loan Application JavaScript Handler
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('carLoanForm');
    const submitBtn = document.getElementById('submitBtn');
    const messageArea = document.getElementById('messageArea');
    const emiInfo = document.getElementById('emiInfo');
    const emiDetails = document.getElementById('emiDetails');

    // Calculate EMI when loan amount or tenure changes
    const loanAmountInput = document.getElementById('loan_amount_required');
    const loanTenureInput = document.getElementById('loan_tenure');

    function calculateEMI() {
        const loanAmount = parseFloat(loanAmountInput.value);
        const tenure = parseFloat(loanTenureInput.value);

        if (loanAmount && tenure && loanAmount >= 50000 && tenure >= 12) {
            fetch('/api/calculate-emi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    loan_type: 'car',
                    loan_amount: loanAmount,
                    tenure: tenure,
                    tenure_unit: 'months'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.emi_info) {
                    const emi = data.emi_info;
                    emiDetails.innerHTML = `
                        <strong>Monthly EMI:</strong> ₹${emi.emi.toLocaleString('en-IN')}<br>
                        <strong>Total Amount:</strong> ₹${emi.total_amount.toLocaleString('en-IN')}<br>
                        <strong>Total Interest:</strong> ₹${emi.total_interest.toLocaleString('en-IN')}<br>
                        <small class="text-muted">Interest Rate: ${emi.interest_rate}% p.a.</small>
                    `;
                    emiInfo.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('EMI calculation error:', error);
            });
        } else {
            emiInfo.style.display = 'none';
        }
    }

    loanAmountInput.addEventListener('input', calculateEMI);
    loanTenureInput.addEventListener('input', calculateEMI);

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';

        // Collect form data
        const monthlyIncome = document.getElementById('monthly_income').value;
        const annualIncome = document.getElementById('annual_income').value;
        const downPayment = document.getElementById('down_payment').value;
        
        const formData = {
            full_name: document.getElementById('full_name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            phone_number: document.getElementById('phone_number').value,
            email: document.getElementById('email').value,
            employment_type: document.getElementById('employment_type').value,
            work_experience: parseFloat(document.getElementById('work_experience').value),
            car_type: document.getElementById('car_type').value,
            brand: document.getElementById('brand').value,
            model: document.getElementById('model').value,
            car_price: parseFloat(document.getElementById('car_price').value),
            registration_city: document.getElementById('registration_city').value,
            loan_amount_required: parseFloat(document.getElementById('loan_amount_required').value),
            loan_tenure: parseInt(document.getElementById('loan_tenure').value),
            down_payment: downPayment === '' ? 0 : parseFloat(downPayment),
            existing_loans: document.getElementById('existing_loans').value
        };

        // Add income (either monthly or annual)
        if (monthlyIncome) {
            formData.monthly_income = parseFloat(monthlyIncome);
        }
        if (annualIncome) {
            formData.annual_income = parseFloat(annualIncome);
        }

        // Handle optional credit score
        const creditScore = document.getElementById('credit_score').value;
        if (creditScore) {
            formData.credit_score = parseInt(creditScore);
        }

        try {
            const response = await fetch('/api/apply/car-loan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show success message
                messageArea.innerHTML = `
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <h5><i class="fas fa-check-circle me-2"></i>Application Submitted Successfully!</h5>
                        <p class="mb-2"><strong>Application ID:</strong> ${data.application_id}</p>
                        ${data.emi_info ? `
                            <hr>
                            <h6>Loan Details:</h6>
                            <ul class="mb-0">
                                <li><strong>Monthly EMI:</strong> ₹${data.emi_info.emi.toLocaleString('en-IN')}</li>
                                <li><strong>Total Amount:</strong> ₹${data.emi_info.total_amount.toLocaleString('en-IN')}</li>
                                <li><strong>Interest Rate:</strong> ${data.emi_info.interest_rate}% p.a.</li>
                            </ul>
                        ` : ''}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                messageArea.style.display = 'block';
                form.reset();
                emiInfo.style.display = 'none';
                
                // Scroll to message
                messageArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                throw new Error(data.error || 'Application submission failed');
            }
        } catch (error) {
            console.error('Error:', error);
            messageArea.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <h5><i class="fas fa-exclamation-circle me-2"></i>Error</h5>
                    <p class="mb-0">${error.message || 'An error occurred while submitting your application. Please try again.'}</p>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            messageArea.style.display = 'block';
            messageArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Submit Application';
        }
    });

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

