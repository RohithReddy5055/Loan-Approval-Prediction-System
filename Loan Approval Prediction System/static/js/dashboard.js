/**
 * Dashboard JavaScript for Model Performance Visualization
 */

let statusDistributionChart = null;
let loanTypeStatusChart = null;
let loanTypeDistributionChart = null;
let loanAmountByTypeChart = null;
let genderDistributionChart = null;
let employmentDistributionChart = null;
let incomeDistributionChart = null;
let creditScoreDistributionChart = null;
let approvalRateByTypeChart = null;
let incomeVsLoanScatterChart = null;
let cachedModels = {};

const LOAN_TYPE_LABELS = {
    education: 'Education',
    home: 'Home',
    car: 'Car',
    personal: 'Personal',
    business: 'Business',
    other: 'Other'
};

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

/**
 * Load dashboard data from API
 */
async function loadDashboardData() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const dashboardContent = document.getElementById('dashboardContent');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    
    try {
        const [performanceResponse, applicationsResponse] = await Promise.all([
            fetch('/api/model/performance'),
            fetch('/api/applications')
        ]);
        
        if (!performanceResponse.ok) throw new Error('Failed to load model performance');
        if (!applicationsResponse.ok) throw new Error('Failed to load applications data');
        
        const [performanceData, applicationsData] = await Promise.all([
            performanceResponse.json(),
            applicationsResponse.json()
        ]);
        
        // Display data
        displayDashboard(performanceData, applicationsData.applications || []);
        
        // Hide loading, show content
        loadingIndicator.style.display = 'none';
        dashboardContent.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        loadingIndicator.style.display = 'none';
        errorMessage.textContent = error.message || 'Failed to load dashboard data';
        errorAlert.style.display = 'block';
    }
}

/**
 * Display dashboard data
 */
function displayDashboard(performanceData, applications) {
    cachedModels = performanceData.models || {};
    // Set best model name
    document.getElementById('bestModelName').textContent = performanceData.best_model || 'N/A';
    
    // Display metrics cards
    displayMetricsCards(performanceData.models);
    
    // Display confusion matrices
    displayConfusionMatrices(performanceData.models);
    
    // Display application loan prediction status insights
    displayLoanStatusSummary(applications);
    renderApplicationInsights(applications);
}

/**
 * Display metrics cards
 */
function displayMetricsCards(models) {
    const container = document.getElementById('metricsCards');
    container.innerHTML = '';
    
    const metrics = ['accuracy', 'precision', 'recall', 'f1_score'];
    const metricLabels = {
        'accuracy': 'Accuracy',
        'precision': 'Precision',
        'recall': 'Recall',
        'f1_score': 'F1 Score'
    };
    
    const colors = ['primary', 'success', 'info', 'warning'];
    
    metrics.forEach((metric, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-3 mb-3';
        
        let maxValue = 0;
        let bestModel = '';
        
        Object.entries(models).forEach(([modelName, modelData]) => {
            if (modelData[metric] > maxValue) {
                maxValue = modelData[metric];
                bestModel = modelName;
            }
        });
        
        col.innerHTML = `
            <div class="card metric-card shadow border-${colors[index]}">
                <div class="card-body text-center">
                    <div class="metric-value">${(maxValue * 100).toFixed(2)}%</div>
                    <div class="metric-label">${metricLabels[metric]}</div>
                    <small class="text-muted">${bestModel}</small>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}


/**
 * Display confusion matrices
 */
function displayConfusionMatrices(models) {
    const container = document.getElementById('confusionMatrices');
    container.innerHTML = '<div class="col-12 mb-3"><h5 class="mb-3"><i class="fas fa-table me-2"></i>Confusion Matrices</h5></div>';
    
    Object.entries(models).forEach(([modelName, modelData]) => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-4';
        
        const cm = modelData.confusion_matrix;
        const [tn, fp, fn, tp] = [cm[0][0], cm[0][1], cm[1][0], cm[1][1]];
        
        col.innerHTML = `
            <div class="card shadow">
                <div class="card-header bg-secondary text-white">
                    <h6 class="mb-0">${modelName}</h6>
                </div>
                <div class="card-body text-center">
                    <table class="confusion-matrix mx-auto">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Predicted: No</th>
                                <th>Predicted: Yes</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th>Actual: No</th>
                                <td class="true-negative">${tn}</td>
                                <td class="false-positive">${fp}</td>
                            </tr>
                            <tr>
                                <th>Actual: Yes</th>
                                <td class="false-negative">${fn}</td>
                                <td class="true-positive">${tp}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

/**
 * Display status summary for all applications
 */
function displayLoanStatusSummary(applications) {
    const summaryContainer = document.getElementById('statusSummaryCards');
    if (!summaryContainer) return;
    
    const statusCounts = getStatusCounts(applications);
    const total = applications.length || 1;
    
    const cardMeta = [
        { status: 'approved', label: 'Approved', color: 'success', icon: 'fa-check-circle' },
        { status: 'rejected', label: 'Rejected', color: 'danger', icon: 'fa-times-circle' },
        { status: 'pending', label: 'Pending', color: 'warning', icon: 'fa-hourglass-half' },
        { status: 'total', label: 'Total Applications', color: 'primary', icon: 'fa-users' },
    ];
    
    summaryContainer.innerHTML = '';
    cardMeta.forEach(meta => {
        let value = 0;
        let percentage = 0;
        if (meta.status === 'total') {
            value = applications.length;
            percentage = 100;
        } else {
            value = statusCounts[meta.status] || 0;
            percentage = (value / total) * 100;
        }
        
        const col = document.createElement('div');
        col.className = 'col-md-3 mb-3';
        col.innerHTML = `
            <div class="card shadow border-${meta.color}">
                <div class="card-body text-center">
                    <i class="fas ${meta.icon} fa-2x text-${meta.color} mb-2"></i>
                    <h4 class="mb-1">${value.toLocaleString()}</h4>
                    <p class="text-muted mb-1">${meta.label}</p>
                    <small class="text-muted">${percentage.toFixed(1)}%</small>
                </div>
            </div>
        `;
        summaryContainer.appendChild(col);
    });
    
    createStatusDistributionChart(statusCounts);
    createLoanTypeStatusChart(applications);
}

function getStatusCounts(applications) {
    const counts = { approved: 0, rejected: 0, pending: 0 };
    applications.forEach(app => {
        const status = (app.status || 'pending').toLowerCase();
        if (counts[status] === undefined) {
            counts[status] = 0;
        }
        counts[status] += 1;
    });
    return counts;
}

function createStatusDistributionChart(statusCounts) {
    const ctx = document.getElementById('statusDistributionChart').getContext('2d');
    const labels = ['Approved', 'Rejected', 'Pending'];
    const dataValues = [
        statusCounts.approved || 0,
        statusCounts.rejected || 0,
        statusCounts.pending || 0
    ];
    const colors = [
        'rgba(25, 135, 84, 0.8)',
        'rgba(220, 53, 69, 0.8)',
        'rgba(255, 193, 7, 0.8)'
    ];
    
    if (statusDistributionChart) {
        statusDistributionChart.destroy();
    }
    
    statusDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: dataValues,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.8', '1')),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                title: {
                    display: true,
                    text: 'Overall Decision Distribution'
                }
            }
        }
    });
}

function createLoanTypeStatusChart(applications) {
    const ctx = document.getElementById('loanTypeStatusChart').getContext('2d');
    const loanTypes = ['education', 'home', 'car', 'personal', 'business'];
    const statusList = ['approved', 'rejected', 'pending'];
    const colors = {
        approved: 'rgba(25, 135, 84, 0.8)',
        rejected: 'rgba(220, 53, 69, 0.8)',
        pending: 'rgba(255, 193, 7, 0.8)'
    };
    
    const countsByType = loanTypes.reduce((acc, type) => {
        acc[type] = { approved: 0, rejected: 0, pending: 0 };
        return acc;
    }, {});
    
    applications.forEach(app => {
        const type = (app.loan_type || '').toLowerCase();
        const status = (app.status || 'pending').toLowerCase();
        if (!countsByType[type]) {
            countsByType[type] = { approved: 0, rejected: 0, pending: 0 };
        }
        if (!countsByType[type][status] && countsByType[type][status] !== 0) {
            countsByType[type][status] = 0;
        }
        countsByType[type][status] += 1;
    });
    
    const datasets = statusList.map(status => ({
        label: status.charAt(0).toUpperCase() + status.slice(1),
        data: loanTypes.map(type => (countsByType[type]?.[status] || 0)),
        backgroundColor: colors[status],
        stack: 'Status'
    }));
    
    if (loanTypeStatusChart) {
        loanTypeStatusChart.destroy();
    }
    
    loanTypeStatusChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: loanTypes.map(type => type.charAt(0).toUpperCase() + type.slice(1)),
            datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                title: {
                    display: true,
                    text: 'Loan Type vs Decision Status'
                }
            },
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        precision:0
                    }
                }
            }
        }
    });
}

/**
 * Render additional analytics visualizations
 */
function renderApplicationInsights(applications) {
    if (!applications || applications.length === 0) {
        const infoCards = document.getElementById('statusSummaryCards');
        if (infoCards) {
            infoCards.insertAdjacentHTML('afterend', `
                <div class="alert alert-info">No application data available to render insights.</div>
            `);
        }
        return;
    }
    
    const analytics = calculateApplicationAnalytics(applications);
    
    createLoanTypeDistributionChart(analytics.loanTypeCounts);
    createLoanAmountByTypeChart(analytics.loanTypeAverageAmounts);
    createGenderDistributionChart(analytics.genderCounts);
    createEmploymentDistributionChart(analytics.employmentCounts);
    createIncomeDistributionChart(analytics.incomeBins);
    createCreditScoreDistributionChart(analytics.creditScoreBins);
    createApprovalRateByTypeChart(analytics.approvalRates);
    createIncomeVsLoanScatterChart(analytics.scatterPoints);
}

function calculateApplicationAnalytics(applications) {
    const loanTypeCounts = {};
    const loanAmountSums = {};
    const loanAmountCounts = {};
    const loanTypeApprovals = {};
    const genderCounts = {};
    const employmentCounts = {};
    const scatterPoints = [];
    
    const incomeBins = [
        { label: '< ₹2L', min: 0, max: 200000, count: 0 },
        { label: '₹2L - ₹5L', min: 200000, max: 500000, count: 0 },
        { label: '₹5L - ₹10L', min: 500000, max: 1000000, count: 0 },
        { label: '₹10L - ₹20L', min: 1000000, max: 2000000, count: 0 },
        { label: '₹20L+', min: 2000000, max: Infinity, count: 0 }
    ];
    
    const creditScoreBins = [
        { label: '< 600', min: 0, max: 600, count: 0 },
        { label: '600 - 700', min: 600, max: 700, count: 0 },
        { label: '700 - 800', min: 700, max: 800, count: 0 },
        { label: '800+', min: 800, max: Infinity, count: 0 }
    ];
    
    applications.forEach(app => {
        const type = normalizeLoanType(app.loan_type);
        const amount = extractLoanAmount(app);
        const income = extractApplicantIncome(app);
        const credit = extractCreditScore(app);
        const status = (app.status || 'pending').toLowerCase();
        const gender = formatLabel(app.gender || 'Unknown');
        const employment = formatLabel(app.employment_type || app.employment_status || 'Unknown');
        
        loanTypeCounts[type] = (loanTypeCounts[type] || 0) + 1;
        if (status === 'approved') {
            loanTypeApprovals[type] = (loanTypeApprovals[type] || 0) + 1;
        }
        
        if (amount !== null) {
            loanAmountSums[type] = (loanAmountSums[type] || 0) + amount;
            loanAmountCounts[type] = (loanAmountCounts[type] || 0) + 1;
        }
        
        if (income !== null) {
            const bin = incomeBins.find(b => income >= b.min && income < b.max);
            if (bin) {
                bin.count += 1;
            }
        }
        
        if (credit !== null) {
            const cbin = creditScoreBins.find(b => credit >= b.min && credit < b.max);
            if (cbin) {
                cbin.count += 1;
            }
        }
        
        genderCounts[gender] = (genderCounts[gender] || 0) + 1;
        employmentCounts[employment] = (employmentCounts[employment] || 0) + 1;
        
        if (income !== null && amount !== null) {
            scatterPoints.push({
                x: +(income / 100000).toFixed(2),
                y: +(amount / 100000).toFixed(2),
                rawIncome: income,
                rawLoan: amount,
                type: LOAN_TYPE_LABELS[type] || type
            });
        }
    });
    
    const loanTypeAverageAmounts = Object.keys(loanAmountSums).reduce((acc, type) => {
        acc[type] = loanAmountCounts[type] ? loanAmountSums[type] / loanAmountCounts[type] : 0;
        return acc;
    }, {});
    
    const approvalRates = Object.keys(loanTypeCounts).map(type => ({
        type,
        rate: loanTypeCounts[type] ? ((loanTypeApprovals[type] || 0) / loanTypeCounts[type]) * 100 : 0
    }));
    
    return {
        loanTypeCounts,
        loanTypeAverageAmounts,
        genderCounts,
        employmentCounts,
        incomeBins,
        creditScoreBins,
        approvalRates,
        scatterPoints
    };
}

function normalizeLoanType(type) {
    const key = (type || 'other').toLowerCase();
    return LOAN_TYPE_LABELS[key] ? key : 'other';
}

function extractLoanAmount(app) {
    const amountFields = [
        'loan_amount_required',
        'loan_amount',
        'loan_amount_requested',
        'loan_amount_applied',
        'loan_amount_needed'
    ];
    for (const field of amountFields) {
        const value = parseNumeric(app[field]);
        if (value !== null) {
            return value;
        }
    }
    return null;
}

function extractApplicantIncome(app) {
    const incomeFields = [
        { key: 'applicant_annual_income', factor: 1 },
        { key: 'parent_guardian_income', factor: 1 },
        { key: 'annual_income', factor: 1 },
        { key: 'co_applicant_income', factor: 1 },
        { key: 'business_income', factor: 1 },
        { key: 'annual_turnover', factor: 1 },
        { key: 'monthly_income', factor: 12 },
        { key: 'monthly_salary', factor: 12 }
    ];
    
    for (const field of incomeFields) {
        const value = parseNumeric(app[field.key]);
        if (value !== null) {
            return value * field.factor;
        }
    }
    return null;
}

function extractCreditScore(app) {
    const fields = ['credit_score', 'credit_history', 'cibil_score'];
    for (const field of fields) {
        const value = parseNumeric(app[field]);
        if (value !== null) {
            return value;
        }
    }
    return null;
}

function parseNumeric(value) {
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
}

function formatLabel(label) {
    if (!label) return 'Unknown';
    return label.toString().trim().split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function createLoanTypeDistributionChart(counts) {
    const canvas = document.getElementById('loanTypeDistributionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const types = Object.keys(counts);
    const values = types.map(t => counts[t]);
    
    if (loanTypeDistributionChart) {
        loanTypeDistributionChart.destroy();
    }
    
    loanTypeDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: types.map(t => LOAN_TYPE_LABELS[t] || t),
            datasets: [{
                data: values,
                backgroundColor: [
                    '#0d6efd',
                    '#6610f2',
                    '#198754',
                    '#fd7e14',
                    '#20c997',
                    '#6c757d'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Share of Applications by Loan Type' }
            }
        }
    });
}

function createLoanAmountByTypeChart(avgAmounts) {
    const canvas = document.getElementById('loanAmountByTypeChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const types = Object.keys(avgAmounts);
    const values = types.map(t => avgAmounts[t] / 100000); // in Lakhs
    
    if (loanAmountByTypeChart) {
        loanAmountByTypeChart.destroy();
    }
    
    loanAmountByTypeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: types.map(t => LOAN_TYPE_LABELS[t] || t),
            datasets: [{
                label: 'Avg Loan Amount (₹ Lakhs)',
                data: values,
                backgroundColor: 'rgba(108, 117, 125, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Average Loan Amount by Type' },
                tooltip: {
                    callbacks: {
                        label: ctx => `₹ ${(ctx.parsed.y * 100000).toLocaleString('en-IN')}`
                    }
                }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createGenderDistributionChart(counts) {
    const canvas = document.getElementById('genderDistributionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = Object.keys(counts);
    const values = labels.map(label => counts[label]);
    
    if (genderDistributionChart) {
        genderDistributionChart.destroy();
    }
    
    genderDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#fd7e14',
                    '#0dcaf0',
                    '#6f42c1',
                    '#adb5bd'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Applicant Gender Mix' }
            }
        }
    });
}

function createEmploymentDistributionChart(counts) {
    const canvas = document.getElementById('employmentDistributionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = Object.keys(counts);
    const values = labels.map(label => counts[label]);
    
    if (employmentDistributionChart) {
        employmentDistributionChart.destroy();
    }
    
    employmentDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Applications',
                data: values,
                backgroundColor: 'rgba(33, 37, 41, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Employment Type Distribution' }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        }
    });
}

function createIncomeDistributionChart(bins) {
    const canvas = document.getElementById('incomeDistributionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = bins.map(bin => bin.label);
    const values = bins.map(bin => bin.count);
    
    if (incomeDistributionChart) {
        incomeDistributionChart.destroy();
    }
    
    incomeDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Applicants',
                data: values,
                backgroundColor: 'rgba(25, 135, 84, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Applicant Income Distribution' }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        }
    });
}

function createCreditScoreDistributionChart(bins) {
    const canvas = document.getElementById('creditScoreDistributionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = bins.map(bin => bin.label);
    const values = bins.map(bin => bin.count);
    
    if (creditScoreDistributionChart) {
        creditScoreDistributionChart.destroy();
    }
    
    creditScoreDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Applicants',
                data: values,
                backgroundColor: 'rgba(102, 16, 242, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Credit Score Buckets' }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        }
    });
}

function createApprovalRateByTypeChart(approvalRates) {
    const canvas = document.getElementById('approvalRateByTypeChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = approvalRates.map(item => LOAN_TYPE_LABELS[item.type] || item.type);
    const values = approvalRates.map(item => item.rate);
    
    if (approvalRateByTypeChart) {
        approvalRateByTypeChart.destroy();
    }
    
    approvalRateByTypeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Approval Rate (%)',
                data: values,
                backgroundColor: 'rgba(13, 202, 240, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Approval Rate by Loan Type' },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.parsed.y.toFixed(1)}%`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: value => `${value}%`
                    }
                }
            }
        }
    });
}

function createIncomeVsLoanScatterChart(points) {
    const canvas = document.getElementById('incomeVsLoanScatterChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (incomeVsLoanScatterChart) {
        incomeVsLoanScatterChart.destroy();
    }
    
    incomeVsLoanScatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Applicants',
                data: points,
                backgroundColor: 'rgba(220, 53, 69, 0.8)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Income vs Loan Amount (₹ Lakhs)' },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const income = (ctx.raw.rawIncome || 0).toLocaleString('en-IN');
                            const loan = (ctx.raw.rawLoan || 0).toLocaleString('en-IN');
                            return `Income: ₹${income}, Loan: ₹${loan} (${ctx.raw.type})`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Income (₹ Lakhs)' }
                },
                y: {
                    title: { display: true, text: 'Loan Amount (₹ Lakhs)' }
                }
            }
        }
    });
}

