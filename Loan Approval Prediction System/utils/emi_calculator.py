"""
EMI (Equated Monthly Installment) Calculator utility.
"""

import math
from typing import Dict, Optional


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> Dict:
    """
    Calculate EMI and related details.
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (as percentage, e.g., 10 for 10%)
        tenure_months: Loan tenure in months
    
    Returns:
        Dictionary with EMI, total amount, total interest, and monthly breakdown
    """
    if principal <= 0 or tenure_months <= 0:
        return {
            'emi': 0,
            'total_amount': 0,
            'total_interest': 0,
            'error': 'Invalid input: Principal and tenure must be positive'
        }
    
    # Convert annual rate to monthly rate (decimal)
    monthly_rate = (annual_rate / 100) / 12
    
    # Calculate EMI using formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    
    total_amount = emi * tenure_months
    total_interest = total_amount - principal
    
    return {
        'emi': round(emi, 2),
        'total_amount': round(total_amount, 2),
        'total_interest': round(total_interest, 2),
        'principal': principal,
        'annual_rate': annual_rate,
        'tenure_months': tenure_months,
        'error': None
    }


def calculate_emi_for_loan_type(loan_type: str, loan_amount: float, tenure: int, tenure_unit: str = 'years') -> Dict:
    """
    Calculate EMI for different loan types with typical interest rates.
    
    Args:
        loan_type: Type of loan (education, home, car, personal, business)
        loan_amount: Loan amount
        tenure: Loan tenure
        tenure_unit: 'years' or 'months'
    
    Returns:
        Dictionary with EMI calculation results
    """
    # Typical interest rates (can be customized)
    interest_rates = {
        'education': 8.5,   # Education loans typically have lower rates
        'home': 9.0,        # Home loans
        'car': 10.5,        # Car loans
        'personal': 12.0,   # Personal loans (higher risk)
        'business': 11.5    # Business loans
    }
    
    # Convert tenure to months if needed
    if tenure_unit == 'years':
        tenure_months = tenure * 12
    else:
        tenure_months = tenure
    
    rate = interest_rates.get(loan_type.lower(), 10.0)  # Default 10% if type not found
    
    result = calculate_emi(loan_amount, rate, tenure_months)
    result['loan_type'] = loan_type
    result['interest_rate'] = rate
    
    return result


def get_loan_details(loan_type: str) -> Dict:
    """Get typical loan details for a loan type."""
    details = {
        'education': {
            'min_amount': 10000,
            'max_amount': 5000000,
            'min_tenure_years': 1,
            'max_tenure_years': 20,
            'typical_rate': 8.5,
            'description': 'Education loans help finance your studies'
        },
        'home': {
            'min_amount': 500000,
            'max_amount': 50000000,
            'min_tenure_years': 5,
            'max_tenure_years': 30,
            'typical_rate': 9.0,
            'description': 'Home loans for buying or constructing your dream home'
        },
        'car': {
            'min_amount': 50000,
            'max_amount': 10000000,
            'min_tenure_years': 1,
            'max_tenure_years': 7,
            'typical_rate': 10.5,
            'description': 'Car loans for new or used vehicles'
        },
        'personal': {
            'min_amount': 10000,
            'max_amount': 5000000,
            'min_tenure_months': 6,
            'max_tenure_months': 60,
            'typical_rate': 12.0,
            'description': 'Personal loans for various purposes'
        },
        'business': {
            'min_amount': 100000,
            'max_amount': 50000000,
            'min_tenure_years': 1,
            'max_tenure_years': 10,
            'typical_rate': 11.5,
            'description': 'Business loans to grow your enterprise'
        }
    }
    
    return details.get(loan_type.lower(), {})

