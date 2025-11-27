"""
Tests for input validation.
"""

import pytest
from utils.validators import LoanApplicationValidator


class TestLoanApplicationValidator:
    """Test cases for LoanApplicationValidator."""
    
    def test_valid_application(self):
        """Test validation of valid application."""
        valid_data = {
            'Gender': 'Male',
            'Married': 'Yes',
            'Dependents': '0',
            'Education': 'Graduate',
            'Self_Employed': 'No',
            'ApplicantIncome': 5000,
            'CoapplicantIncome': 2000,
            'LoanAmount': 150000,
            'Loan_Amount_Term': 360,
            'Credit_History': 1.0,
            'Property_Area': 'Urban'
        }
        
        is_valid, error = LoanApplicationValidator.validate_application(valid_data)
        assert is_valid == True
        assert error is None
    
    def test_missing_field(self):
        """Test validation with missing field."""
        invalid_data = {
            'Gender': 'Male',
            # Missing other required fields
        }
        
        is_valid, error = LoanApplicationValidator.validate_application(invalid_data)
        assert is_valid == False
        assert error is not None
    
    def test_invalid_gender(self):
        """Test validation with invalid gender."""
        invalid_data = {
            'Gender': 'Invalid',
            'Married': 'Yes',
            'Dependents': '0',
            'Education': 'Graduate',
            'Self_Employed': 'No',
            'ApplicantIncome': 5000,
            'CoapplicantIncome': 2000,
            'LoanAmount': 150000,
            'Loan_Amount_Term': 360,
            'Credit_History': 1.0,
            'Property_Area': 'Urban'
        }
        
        is_valid, error = LoanApplicationValidator.validate_application(invalid_data)
        assert is_valid == False
        assert 'Gender' in error
    
    def test_invalid_income(self):
        """Test validation with invalid income."""
        invalid_data = {
            'Gender': 'Male',
            'Married': 'Yes',
            'Dependents': '0',
            'Education': 'Graduate',
            'Self_Employed': 'No',
            'ApplicantIncome': -1000,  # Invalid negative income
            'CoapplicantIncome': 2000,
            'LoanAmount': 150000,
            'Loan_Amount_Term': 360,
            'Credit_History': 1.0,
            'Property_Area': 'Urban'
        }
        
        is_valid, error = LoanApplicationValidator.validate_application(invalid_data)
        assert is_valid == False
        assert 'ApplicantIncome' in error
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        raw_data = {
            'Gender': '  male  ',
            'Married': 'yes',
            'ApplicantIncome': '5000',
            'LoanAmount': 150000.5
        }
        
        sanitized = LoanApplicationValidator.sanitize_input(raw_data)
        
        assert sanitized['Gender'] == 'male'
        assert sanitized['Married'] == 'yes'
        assert isinstance(sanitized['ApplicantIncome'], float)
        assert isinstance(sanitized['LoanAmount'], float)

