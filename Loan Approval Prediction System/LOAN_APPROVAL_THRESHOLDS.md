# Loan Approval Threshold Values - Complete Analysis

This document provides a comprehensive breakdown of all approval and rejection threshold values for each loan type in the system.

---

## 📚 **1. EDUCATION LOAN**

### ✅ **Approval Criteria (ALL must be met):**

| Criteria | Threshold Value | Description |
|----------|----------------|-------------|
| **Age** | ≥ 18 years | Minimum applicant age |
| **Applicant Income** | ≥ ₹0/year | No minimum (students can have ₹0 income) |
| **Parent/Guardian Income** | ≥ ₹1,50,000/year | Minimum parent income required |
| **Combined Income** | ≥ ₹1,50,000/year | Applicant + Parent income combined |
| **Course Name** | Valid (≥ 3 characters) | Must be a valid course name |
| **Institution Name** | Valid (≥ 3 characters) | Must be a valid institution name |
| **Credit History** | ≥ 0.5 (if provided) | Optional field, but if provided must be ≥ 0.5 |
| **Loan Amount vs Income** | ≤ 15 × Parent Income | Loan cannot exceed 15 times parent income |
| **Maximum Loan Amount** | ≤ ₹15,00,000 | Absolute maximum loan limit (₹15 Lakhs) |

### ❌ **Rejection Reasons:**

- Age < 18 years
- Applicant income < 0 (negative)
- Parent/Guardian income < ₹1,50,000/year
- Combined income < ₹1,50,000/year
- Invalid or missing course name (< 3 characters)
- Invalid or missing institution name (< 3 characters)
- Credit history < 0.5 (if provided)
- Loan amount > 15 × Parent Income
- Loan amount > ₹15,00,000

---

## 🏠 **2. HOME LOAN**

### ✅ **Approval Criteria (ALL must be met):**

| Criteria | Threshold Value | Description |
|----------|----------------|-------------|
| **Age** | 21-60 years | Age range (inclusive) |
| **Monthly Income** | ≥ ₹35,000/month | Total monthly income (including co-applicant) |
| **Loan Amount (Minimum)** | ≥ ₹5,00,000 | Minimum loan amount |
| **Credit Score** | ≥ 650 | Required credit score |
| **Loan vs Property Value** | ≤ 80% of Property Value | Loan cannot exceed 80% of property value |
| **EMI-to-Income Ratio** | ≤ 40% | Monthly EMI should not exceed 40% of monthly income |

### 📊 **Calculation Details:**
- **Interest Rate**: 9.0% p.a. (used for EMI calculation)
- **Total Monthly Income**: Annual Income ÷ 12 + (Co-applicant Income ÷ 12)
- **EMI Calculation**: Standard EMI formula with 9% annual rate

### ❌ **Rejection Reasons:**

- Age < 21 or Age > 60
- Monthly income < ₹35,000/month
- Loan amount < ₹5,00,000
- Credit score not provided (required field)
- Credit score < 650
- Loan amount > 80% of property value
- EMI-to-income ratio > 40%

---

## 🚗 **3. CAR LOAN**

### ✅ **Approval Criteria (ALL must be met):**

| Criteria | Threshold Value | Description |
|----------|----------------|-------------|
| **Monthly Income** | ≥ ₹20,000/month | Minimum monthly income required |
| **Credit Score** | ≥ 600 | Required credit score |
| **Down Payment** | ≥ 10% of Car Price | Minimum down payment percentage |
| **Work Experience** | ≥ 1 year | Minimum work experience |
| **EMI-to-Income Ratio** | ≤ 40% | Monthly EMI should not exceed 40% of monthly income |

### 📊 **Calculation Details:**
- **Interest Rate**: 10.5% p.a. (used for EMI calculation)
- **Monthly Income**: Uses `monthly_income` field, or calculates from `annual_income ÷ 12`
- **Loan Tenure**: In months (default: 60 months)

### ❌ **Rejection Reasons:**

- Monthly income < ₹20,000/month
- Credit score not provided (required field)
- Credit score < 600
- Down payment < 10% of car price
- Work experience < 1 year
- EMI-to-income ratio > 40%

**Note**: Vehicle age check (< 8 years for used cars) is not currently implemented as it requires year of manufacture data.

---

## 💰 **4. PERSONAL LOAN**

### ✅ **Approval Criteria (ALL must be met):**

| Criteria | Threshold Value | Description |
|----------|----------------|-------------|
| **Monthly Salary** | ≥ ₹25,000/month | Minimum monthly salary required |
| **Credit Score** | ≥ 650 | Required credit score |
| **Work Experience** | ≥ 1 year | Minimum work experience |
| **Loan vs Salary** | ≤ 12 × Monthly Salary | Loan cannot exceed 12 times monthly salary |
| **EMI-to-Income Ratio** | < 50% | Monthly EMI should be less than 50% of monthly income |

### 📊 **Calculation Details:**
- **Interest Rate**: 12.0% p.a. (used for EMI calculation)
- **Loan Tenure**: In months (default: 36 months)
- **Maximum Loan**: Monthly Salary × 12

### ❌ **Rejection Reasons:**

- Monthly salary < ₹25,000/month
- Credit score not provided (required field)
- Credit score < 650
- Work experience < 1 year
- Loan amount > 12 × monthly salary
- EMI-to-income ratio ≥ 50%

---

## 🏢 **5. BUSINESS LOAN**

### ✅ **Approval Criteria (ALL must be met):**

| Criteria | Threshold Value | Description |
|----------|----------------|-------------|
| **Business Age** | ≥ 2 years | Minimum years in business |
| **Annual Turnover** | ≥ ₹10,00,000 | Minimum annual turnover (₹10 Lakhs) |
| **GST Number** | Valid (15 characters) | Must be a valid 15-character GST number |
| **Credit Score** | ≥ 600 | Required credit score |
| **Loan vs Profit** | ≤ 3 × Estimated Annual Profit | Loan cannot exceed 3 times estimated profit |

### 📊 **Calculation Details:**
- **Estimated Profit**: Assumed to be 10% of annual turnover
- **Maximum Loan**: Estimated Profit × 3 = (Turnover × 0.10) × 3
- **Example**: If turnover = ₹10,00,000, estimated profit = ₹1,00,000, max loan = ₹3,00,000

### ❌ **Rejection Reasons:**

- Business age < 2 years
- Annual turnover < ₹10,00,000
- GST number invalid or missing (< 15 characters)
- Credit score not provided (required field)
- Credit score < 600
- Loan amount > 3 × estimated annual profit

**Note**: Profitability check (positive cash flow) is assumed if turnover meets requirements.

---

## 📋 **Summary Table - Quick Reference**

| Loan Type | Min Income | Credit Score | Age Range | EMI Ratio | Special Requirements |
|-----------|-----------|-------------|-----------|-----------|---------------------|
| **Education** | ₹0 (applicant)<br>₹1,50,000 (parent) | ≥ 0.5 (if provided) | ≥ 18 | N/A | Combined income ≥ ₹1,50,000<br>Loan ≤ ₹15 Lakhs |
| **Home** | ₹35,000/month | ≥ 650 | 21-60 | ≤ 40% | Loan ≥ ₹5 Lakhs<br>Loan ≤ 80% property value |
| **Car** | ₹20,000/month | ≥ 600 | N/A | ≤ 40% | Down payment ≥ 10%<br>Work exp ≥ 1 year |
| **Personal** | ₹25,000/month | ≥ 650 | N/A | < 50% | Loan ≤ 12× salary<br>Work exp ≥ 1 year |
| **Business** | ₹10 Lakhs turnover | ≥ 600 | N/A | N/A | Business age ≥ 2 years<br>Valid GST number |

---

## 🔍 **Key Notes:**

1. **Credit Score**: Required for Home, Car, Personal, and Business loans. Optional for Education loans.

2. **EMI Calculation**: 
   - Education: 8.5% p.a.
   - Home: 9.0% p.a.
   - Car: 10.5% p.a.
   - Personal: 12.0% p.a.
   - Business: 11.5% p.a.

3. **Income Calculation**:
   - Home Loan: Includes co-applicant income
   - Car Loan: Uses monthly_income or calculates from annual_income
   - Personal Loan: Uses monthly_income directly

4. **Validation Order**: Checks are performed in sequence, and the first failing check causes immediate rejection with a specific reason.

5. **All Criteria Must Pass**: For approval, ALL criteria for the loan type must be satisfied. If any single criterion fails, the application is rejected.

---

## 📝 **Rejection Message Format:**

When an application is rejected, the system provides specific reasons in the format:
```
"Reason 1; Reason 2; Reason 3"
```

Each reason clearly states:
- What value was provided
- What the minimum/maximum requirement is
- Why it failed

Example:
```
"Monthly income (₹30,000) is below minimum requirement (₹35,000/month); Credit score (600) is below minimum requirement (650)"
```

---

**Last Updated**: Based on current codebase analysis
**File Location**: `utils/approval_engine.py`

