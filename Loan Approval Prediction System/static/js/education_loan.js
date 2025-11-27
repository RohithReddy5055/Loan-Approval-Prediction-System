/**
 * Education Loan Application JavaScript Handler
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('educationLoanForm');
    const submitBtn = document.getElementById('submitBtn');
    const messageArea = document.getElementById('messageArea');
    const emiInfo = document.getElementById('emiInfo');
    const emiDetails = document.getElementById('emiDetails');

    // Calculate EMI when loan amount or repayment period changes
    const loanAmountInput = document.getElementById('loan_amount_required');
    const repaymentPeriodInput = document.getElementById('repayment_period');

    function calculateEMI() {
        const loanAmount = parseFloat(loanAmountInput.value);
        const tenure = parseFloat(repaymentPeriodInput.value);

        if (loanAmount && tenure && loanAmount >= 10000 && tenure >= 1) {
            fetch('/api/calculate-emi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    loan_type: 'education',
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
    repaymentPeriodInput.addEventListener('input', calculateEMI);

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
        const applicantIncome = document.getElementById('applicant_annual_income').value;
        const parentIncome = document.getElementById('parent_guardian_income').value;
        const coBorrowerIncome = document.getElementById('co_borrower_annual_income').value;
        
        const formData = {
            full_name: document.getElementById('full_name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            phone_number: document.getElementById('phone_number').value,
            email: document.getElementById('email').value,
            course_name: document.getElementById('course_name').value,
            course_duration: parseInt(document.getElementById('course_duration').value),
            institution_name: document.getElementById('institution_name').value,
            institution_type: document.getElementById('institution_type').value,
            applicant_annual_income: applicantIncome === '' ? 0 : parseFloat(applicantIncome),  // Allow 0 for students
            parent_guardian_income: parentIncome === '' ? 0 : parseFloat(parentIncome),
            co_borrower_name: document.getElementById('co_borrower_name').value,
            co_borrower_occupation: document.getElementById('co_borrower_occupation').value,
            co_borrower_annual_income: coBorrowerIncome === '' ? 0 : parseFloat(coBorrowerIncome),
            existing_loan: document.getElementById('existing_loan').value,
            loan_amount_required: parseFloat(document.getElementById('loan_amount_required').value),
            repayment_period: parseInt(document.getElementById('repayment_period').value),
            purpose: document.getElementById('purpose').value
        };

        // Handle file upload (if any)
        const admissionProof = document.getElementById('admission_proof').files[0];
        if (admissionProof) {
            formData.admission_proof_filename = admissionProof.name;
        }

        try {
            const response = await fetch('/api/apply/education-loan', {
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

