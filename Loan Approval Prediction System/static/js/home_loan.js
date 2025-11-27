/**
 * Home Loan Application JavaScript Handler
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('homeLoanForm');
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

        if (loanAmount && tenure && loanAmount >= 500000 && tenure >= 5) {
            fetch('/api/calculate-emi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    loan_type: 'home',
                    loan_amount: loanAmount,
                    tenure: tenure,
                    tenure_unit: 'years'
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
        const coApplicantIncome = document.getElementById('co_applicant_income').value;
        const downPayment = document.getElementById('down_payment_amount').value;
        
        const formData = {
            full_name: document.getElementById('full_name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            marital_status: document.getElementById('marital_status').value,
            phone_number: document.getElementById('phone_number').value,
            email: document.getElementById('email').value,
            employment_type: document.getElementById('employment_type').value,
            company_business_name: document.getElementById('company_business_name').value,
            work_experience: parseFloat(document.getElementById('work_experience').value),
            annual_income: parseFloat(document.getElementById('annual_income').value),
            property_type: document.getElementById('property_type').value,
            property_location: document.getElementById('property_location').value,
            property_value: parseFloat(document.getElementById('property_value').value),
            ownership_type: document.getElementById('ownership_type').value,
            down_payment_amount: downPayment === '' ? 0 : parseFloat(downPayment),
            co_applicant_income: coApplicantIncome === '' ? 0 : parseFloat(coApplicantIncome),
            existing_emi: document.getElementById('existing_emi').value,
            loan_amount_required: parseFloat(document.getElementById('loan_amount_required').value),
            loan_tenure: parseInt(document.getElementById('loan_tenure').value)
        };

        // Handle optional fields
        const builderName = document.getElementById('builder_name').value;
        if (builderName) {
            formData.builder_name = builderName;
        }

        const creditScore = document.getElementById('credit_score').value;
        if (creditScore) {
            formData.credit_score = parseInt(creditScore);
        }

        // Handle file uploads (if any)
        const bankStatement = document.getElementById('bank_statement').files[0];
        if (bankStatement) {
            formData.bank_statement_filename = bankStatement.name;
        }

        try {
            const response = await fetch('/api/apply/home-loan', {
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

