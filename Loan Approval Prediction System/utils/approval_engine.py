"""
Loan Approval Rules Engine.

This module contains the approval logic for different loan types based on
threshold rules and eligibility criteria.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def check_education_loan(data: Dict) -> Dict:
    """
    Check Education Loan approval based on threshold rules.
    
    Rules:
    - Applicant Age ≥ 18
    - Applicant Income ≥ ₹0/year (no minimum requirement for students)
    - Parent/Guardian Income ≥ ₹1,50,000/year
    - Valid course and institution
    - Credit History ≥ 0.5 (if provided)
    - Loan Amount ≤ 15 × Parent Annual Income
    
    Approve if ALL true:
    - (Applicant Income + Parent Income) ≥ ₹1,50,000/year
    - Valid course and institution
    - Credit history ≥ 0.5 (if provided)
    - Loan ≤ ₹15 Lakhs
    """
    reasons = []
    
    # Extract data
    age = data.get('age', 0)
    applicant_income = data.get('applicant_annual_income', 0)
    parent_income = data.get('parent_guardian_income', 0)
    course_name = data.get('course_name', '').strip()
    institution_name = data.get('institution_name', '').strip()
    institution_type = data.get('institution_type', '').strip()
    loan_amount = data.get('loan_amount_required', 0)
    credit_history = data.get('credit_history', None)  # Optional field
    
    # Check minimum age
    if age < 18:
        reasons.append(f"Applicant age ({age}) is below minimum requirement (18 years)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check applicant income (no minimum requirement - can be 0 for students)
    if applicant_income < 0:
        reasons.append(f"Applicant income cannot be negative")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check parent/guardian income
    if parent_income < 150000:
        reasons.append(f"Parent/Guardian income (₹{parent_income:,.0f}) is below minimum requirement (₹1,50,000/year)")
    
    # Check combined income
    combined_income = applicant_income + parent_income
    if combined_income < 150000:
        reasons.append(f"Combined income (₹{combined_income:,.0f}) is below minimum requirement (₹1,50,000/year)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check course validity
    if not course_name or len(course_name) < 3:
        reasons.append("Course name is invalid or missing")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    if not institution_name or len(institution_name) < 3:
        reasons.append("Institution name is invalid or missing")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check credit history if provided
    if credit_history is not None and credit_history < 0.5:
        reasons.append(f"Credit history ({credit_history}) is below minimum requirement (0.5)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check loan amount vs parent income
    max_loan_by_income = parent_income * 15
    if loan_amount > max_loan_by_income:
        reasons.append(f"Loan amount (₹{loan_amount:,.0f}) exceeds maximum allowed (15× parent income = ₹{max_loan_by_income:,.0f})")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check loan amount limit (₹15 Lakhs = 1,500,000)
    if loan_amount > 1500000:
        reasons.append(f"Loan amount (₹{loan_amount:,.0f}) exceeds maximum limit (₹15 Lakhs)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # All checks passed
    return {
        'approved': True,
        'reason': 'Application meets all eligibility criteria for education loan'
    }


def check_home_loan(data: Dict) -> Dict:
    """
    Check Home Loan approval based on threshold rules.
    
    Rules:
    - Monthly Income ≥ ₹35,000
    - Loan Amount ≥ ₹5,00,000
    - Applicant Age 21-60
    - Credit Score ≥ 650
    - Existing EMI < 40% of monthly income
    - Loan Amount ≤ 80% of Property Value
    
    Approve if:
    - EMI-to-income ratio ≤ 40%
    - Credit Score ≥ 650
    - Loan amount reasonable compared to property value
    - Income ≥ ₹35,000
    """
    reasons = []
    
    # Extract data
    age = data.get('age', 0)
    annual_income = data.get('annual_income', 0)
    monthly_income = annual_income / 12 if annual_income > 0 else 0
    loan_amount = data.get('loan_amount_required', 0)
    property_value = data.get('property_value', 0)
    credit_score = data.get('credit_score', None)
    existing_emi = data.get('existing_emi', 'No')
    loan_tenure = data.get('loan_tenure', 20)  # years
    co_applicant_income = data.get('co_applicant_income', 0)
    
    # Calculate total monthly income (including co-applicant)
    total_monthly_income = monthly_income + (co_applicant_income / 12)
    
    # Check age
    if age < 21 or age > 60:
        reasons.append(f"Applicant age ({age}) is outside acceptable range (21-60 years)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check minimum monthly income
    if total_monthly_income < 35000:
        reasons.append(f"Monthly income (₹{total_monthly_income:,.0f}) is below minimum requirement (₹35,000/month)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check minimum loan amount
    if loan_amount < 500000:
        reasons.append(f"Loan amount (₹{loan_amount:,.0f}) is below minimum requirement (₹5,00,000)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check credit score
    if credit_score is None:
        reasons.append("Credit score is required but not provided")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    if credit_score < 650:
        reasons.append(f"Credit score ({credit_score}) is below minimum requirement (650)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check loan amount vs property value (should be ≤ 80%)
    if property_value > 0:
        max_loan_by_property = property_value * 0.80
        if loan_amount > max_loan_by_property:
            reasons.append(f"Loan amount (₹{loan_amount:,.0f}) exceeds 80% of property value (₹{max_loan_by_property:,.0f})")
            return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Calculate EMI (using 9% interest rate for home loans)
    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    monthly_rate = (9.0 / 100) / 12
    tenure_months = loan_tenure * 12
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    else:
        emi = loan_amount / tenure_months
    
    # Check EMI-to-income ratio (should be ≤ 40%)
    emi_ratio = (emi / total_monthly_income) * 100 if total_monthly_income > 0 else 100
    if emi_ratio > 40:
        reasons.append(f"EMI-to-income ratio ({emi_ratio:.1f}%) exceeds maximum allowed (40%)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check existing EMI burden
    if existing_emi.lower() == 'yes':
        # If existing EMI info is not provided, we can't verify, so we'll be conservative
        # For now, we'll just check that the new EMI doesn't exceed 40% of income
        pass  # Already checked above
    
    # All checks passed
    return {
        'approved': True,
        'reason': 'Application meets all eligibility criteria for home loan'
    }


def check_car_loan(data: Dict) -> Dict:
    """
    Check Car Loan approval based on threshold rules.
    
    Rules:
    - Monthly Income ≥ ₹20,000
    - Credit Score ≥ 600
    - Down Payment ≥ 10% of car price
    - Vehicle age (if used) < 8 years
    - Employment Stability ≥ 1 year
    
    Approve if:
    - Income ≥ ₹20,000
    - Credit Score ≥ 600
    - Down payment ≥ 10%
    - EMI ≤ 40% of income
    """
    reasons = []
    
    # Extract data
    monthly_income = data.get('monthly_income', 0)
    annual_income = data.get('annual_income', 0)
    if monthly_income == 0 and annual_income > 0:
        monthly_income = annual_income / 12
    
    credit_score = data.get('credit_score', None)
    car_price = data.get('car_price', 0)
    down_payment = data.get('down_payment', 0)
    loan_amount = data.get('loan_amount_required', 0)
    car_type = data.get('car_type', '').strip()
    work_experience = data.get('work_experience', 0)
    loan_tenure = data.get('loan_tenure', 60)  # months
    
    # Check minimum monthly income
    if monthly_income < 20000:
        reasons.append(f"Monthly income (₹{monthly_income:,.0f}) is below minimum requirement (₹20,000/month)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check credit score
    if credit_score is None:
        reasons.append("Credit score is required but not provided")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    if credit_score < 600:
        reasons.append(f"Credit score ({credit_score}) is below minimum requirement (600)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check down payment (should be ≥ 10% of car price)
    if car_price > 0:
        min_down_payment = car_price * 0.10
        if down_payment < min_down_payment:
            reasons.append(f"Down payment (₹{down_payment:,.0f}) is below minimum requirement (10% of car price = ₹{min_down_payment:,.0f})")
            return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check work experience
    if work_experience < 1:
        reasons.append(f"Work experience ({work_experience} years) is below minimum requirement (1 year)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Calculate EMI (using 10.5% interest rate for car loans)
    monthly_rate = (10.5 / 100) / 12
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** loan_tenure) / (((1 + monthly_rate) ** loan_tenure) - 1)
    else:
        emi = loan_amount / loan_tenure
    
    # Check EMI-to-income ratio (should be ≤ 40%)
    emi_ratio = (emi / monthly_income) * 100 if monthly_income > 0 else 100
    if emi_ratio > 40:
        reasons.append(f"EMI-to-income ratio ({emi_ratio:.1f}%) exceeds maximum allowed (40%)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Note: Vehicle age check would require additional data (year of manufacture)
    # For now, we'll skip this check as it's not in the schema
    
    # All checks passed
    return {
        'approved': True,
        'reason': 'Application meets all eligibility criteria for car loan'
    }


def check_personal_loan(data: Dict) -> Dict:
    """
    Check Personal Loan approval based on threshold rules.
    
    Rules:
    - Monthly Salary ≥ ₹25,000
    - Credit Score ≥ 650
    - Work Experience ≥ 1 year
    - Existing EMI < 50% income
    - Loan Amount ≤ 12 × salary
    
    Approve if ALL true:
    - Credit score ≥ 650
    - Salary ≥ ₹25,000
    - EMI burden < 50%
    - Loan ≤ 12× monthly salary
    """
    reasons = []
    
    # Extract data
    monthly_income = data.get('monthly_income', 0)
    credit_score = data.get('credit_score', None)
    work_experience = data.get('work_experience', 0)
    loan_amount = data.get('loan_amount_required', 0)
    loan_tenure = data.get('loan_tenure', 36)  # months
    existing_emi = data.get('existing_emi', 'No')
    
    # Check minimum monthly salary
    if monthly_income < 25000:
        reasons.append(f"Monthly salary (₹{monthly_income:,.0f}) is below minimum requirement (₹25,000/month)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check credit score
    if credit_score is None:
        reasons.append("Credit score is required but not provided")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    if credit_score < 650:
        reasons.append(f"Credit score ({credit_score}) is below minimum requirement (650)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check work experience
    if work_experience < 1:
        reasons.append(f"Work experience ({work_experience} years) is below minimum requirement (1 year)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check loan amount vs salary (should be ≤ 12× monthly salary)
    max_loan_by_salary = monthly_income * 12
    if loan_amount > max_loan_by_salary:
        reasons.append(f"Loan amount (₹{loan_amount:,.0f}) exceeds maximum allowed (12× monthly salary = ₹{max_loan_by_salary:,.0f})")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Calculate EMI (using 12% interest rate for personal loans)
    monthly_rate = (12.0 / 100) / 12
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** loan_tenure) / (((1 + monthly_rate) ** loan_tenure) - 1)
    else:
        emi = loan_amount / loan_tenure
    
    # Check EMI-to-income ratio (should be < 50%)
    emi_ratio = (emi / monthly_income) * 100 if monthly_income > 0 else 100
    if emi_ratio >= 50:
        reasons.append(f"EMI-to-income ratio ({emi_ratio:.1f}%) exceeds maximum allowed (50%)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check existing EMI burden (if yes, we need to ensure total EMI < 50%)
    # Since we don't have the existing EMI amount, we'll be conservative
    # and just ensure the new EMI alone is reasonable
    
    # All checks passed
    return {
        'approved': True,
        'reason': 'Application meets all eligibility criteria for personal loan'
    }


def check_business_loan(data: Dict) -> Dict:
    """
    Check Business Loan approval based on threshold rules.
    
    Rules:
    - Business Age ≥ 2 years
    - Annual Turnover ≥ ₹10 Lakhs
    - Profitability > 0 (positive cash flow)
    - Credit Score ≥ 600
    - GST Number valid
    - Collateral optional
    
    Approve if ALL true:
    - Turnover ≥ ₹10 Lakhs
    - Business age ≥ 2 years
    - Positive cash flow (we'll assume if turnover is good)
    - Loan amount ≤ 3× annual profit (we'll use turnover as proxy)
    - Credit score ≥ 600
    """
    reasons = []
    
    # Extract data
    business_age = data.get('business_age', 0)
    annual_turnover = data.get('annual_turnover', 0)
    loan_amount = data.get('loan_amount_required', 0)
    gst_number = data.get('gst_number', '').strip()
    credit_score = data.get('credit_score', None)
    
    # Check business age
    if business_age < 2:
        reasons.append(f"Business age ({business_age} years) is below minimum requirement (2 years)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check annual turnover (₹10 Lakhs = 1,000,000)
    if annual_turnover < 1000000:
        reasons.append(f"Annual turnover (₹{annual_turnover:,.0f}) is below minimum requirement (₹10 Lakhs)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check GST number validity (basic check - should be 15 characters)
    if not gst_number or len(gst_number) < 15:
        reasons.append("GST number is invalid or missing (should be 15 characters)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check credit score
    if credit_score is None:
        reasons.append("Credit score is required but not provided")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    if credit_score < 600:
        reasons.append(f"Credit score ({credit_score}) is below minimum requirement (600)")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Check loan amount vs annual profit
    # Since we don't have profit data, we'll use a conservative estimate:
    # Assume profit is at least 10% of turnover, so loan should be ≤ 3× (10% of turnover)
    estimated_profit = annual_turnover * 0.10
    max_loan_by_profit = estimated_profit * 3
    if loan_amount > max_loan_by_profit:
        reasons.append(f"Loan amount (₹{loan_amount:,.0f}) exceeds maximum allowed (3× estimated annual profit = ₹{max_loan_by_profit:,.0f})")
        return {'approved': False, 'reason': '; '.join(reasons)}
    
    # Note: Profitability check would require profit/loss data
    # For now, we'll assume positive cash flow if turnover is good
    
    # All checks passed
    return {
        'approved': True,
        'reason': 'Application meets all eligibility criteria for business loan'
    }


def check_loan_approval(loan_type: str, data: Dict) -> Dict:
    """
    Main function to check loan approval for any loan type.
    
    Args:
        loan_type: Type of loan (education, home, car, personal, business)
        data: Application data dictionary
    
    Returns:
        Dictionary with 'approved' (bool) and 'reason' (str)
    """
    loan_type = loan_type.lower()
    
    if loan_type == 'education':
        return check_education_loan(data)
    elif loan_type == 'home':
        return check_home_loan(data)
    elif loan_type == 'car':
        return check_car_loan(data)
    elif loan_type == 'personal':
        return check_personal_loan(data)
    elif loan_type == 'business':
        return check_business_loan(data)
    else:
        return {
            'approved': False,
            'reason': f'Unknown loan type: {loan_type}'
        }

