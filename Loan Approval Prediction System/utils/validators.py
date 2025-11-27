"""
Input validation utilities for loan application data.
"""

import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoanApplicationValidator:
    """Validator for loan application inputs."""
    
    # Valid values for categorical fields
    VALID_GENDERS = ['Male', 'Female']
    VALID_MARRIED = ['Yes', 'No']
    VALID_DEPENDENTS = ['0', '1', '2', '3+']
    VALID_EDUCATION = ['Graduate', 'Not Graduate']
    VALID_SELF_EMPLOYED = ['Yes', 'No']
    VALID_PROPERTY_AREA = ['Urban', 'Rural', 'Semiurban']
    
    # Valid ranges
    MIN_INCOME = 0
    MAX_INCOME = 1000000
    MIN_LOAN_AMOUNT = 0
    MAX_LOAN_AMOUNT = 1000000
    MIN_LOAN_TERM = 12  # months
    MAX_LOAN_TERM = 480  # months (40 years)
    VALID_CREDIT_HISTORY = [0.0, 1.0]
    
    @staticmethod
    def validate_application(data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate loan application data.
        
        Args:
            data: Dictionary containing loan application fields
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = [
            'Gender', 'Married', 'Dependents', 'Education', 
            'Self_Employed', 'ApplicantIncome', 'CoapplicantIncome',
            'LoanAmount', 'Loan_Amount_Term', 'Credit_History', 'Property_Area'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate Gender
        if data['Gender'] not in LoanApplicationValidator.VALID_GENDERS:
            return False, f"Invalid Gender. Must be one of: {LoanApplicationValidator.VALID_GENDERS}"
        
        # Validate Married
        if data['Married'] not in LoanApplicationValidator.VALID_MARRIED:
            return False, f"Invalid Married. Must be one of: {LoanApplicationValidator.VALID_MARRIED}"
        
        # Validate Dependents
        if str(data['Dependents']) not in LoanApplicationValidator.VALID_DEPENDENTS:
            return False, f"Invalid Dependents. Must be one of: {LoanApplicationValidator.VALID_DEPENDENTS}"
        
        # Validate Education
        if data['Education'] not in LoanApplicationValidator.VALID_EDUCATION:
            return False, f"Invalid Education. Must be one of: {LoanApplicationValidator.VALID_EDUCATION}"
        
        # Validate Self_Employed
        if data['Self_Employed'] not in LoanApplicationValidator.VALID_SELF_EMPLOYED:
            return False, f"Invalid Self_Employed. Must be one of: {LoanApplicationValidator.VALID_SELF_EMPLOYED}"
        
        # Validate Property_Area
        if data['Property_Area'] not in LoanApplicationValidator.VALID_PROPERTY_AREA:
            return False, f"Invalid Property_Area. Must be one of: {LoanApplicationValidator.VALID_PROPERTY_AREA}"
        
        # Validate numeric fields
        try:
            applicant_income = float(data['ApplicantIncome'])
            if applicant_income < LoanApplicationValidator.MIN_INCOME or applicant_income > LoanApplicationValidator.MAX_INCOME:
                return False, f"ApplicantIncome must be between {LoanApplicationValidator.MIN_INCOME} and {LoanApplicationValidator.MAX_INCOME}"
            
            coapplicant_income = float(data['CoapplicantIncome'])
            if coapplicant_income < LoanApplicationValidator.MIN_INCOME or coapplicant_income > LoanApplicationValidator.MAX_INCOME:
                return False, f"CoapplicantIncome must be between {LoanApplicationValidator.MIN_INCOME} and {LoanApplicationValidator.MAX_INCOME}"
            
            loan_amount = float(data['LoanAmount'])
            if loan_amount < LoanApplicationValidator.MIN_LOAN_AMOUNT or loan_amount > LoanApplicationValidator.MAX_LOAN_AMOUNT:
                return False, f"LoanAmount must be between {LoanApplicationValidator.MIN_LOAN_AMOUNT} and {LoanApplicationValidator.MAX_LOAN_AMOUNT}"
            
            loan_term = float(data['Loan_Amount_Term'])
            if loan_term < LoanApplicationValidator.MIN_LOAN_TERM or loan_term > LoanApplicationValidator.MAX_LOAN_TERM:
                return False, f"Loan_Amount_Term must be between {LoanApplicationValidator.MIN_LOAN_TERM} and {LoanApplicationValidator.MAX_LOAN_TERM}"
            
            credit_history = float(data['Credit_History'])
            if credit_history not in LoanApplicationValidator.VALID_CREDIT_HISTORY:
                return False, f"Credit_History must be either 0.0 or 1.0"
                
        except (ValueError, TypeError) as e:
            return False, f"Invalid numeric value: {str(e)}"
        
        return True, None
    
    @staticmethod
    def sanitize_input(data: Dict) -> Dict:
        """
        Sanitize and normalize input data.
        
        Args:
            data: Raw input dictionary
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        # String fields - strip whitespace and capitalize
        string_fields = ['Gender', 'Married', 'Education', 'Self_Employed', 'Property_Area']
        for field in string_fields:
            if field in data:
                sanitized[field] = str(data[field]).strip()
        
        # Dependents - convert to string
        if 'Dependents' in data:
            sanitized['Dependents'] = str(data['Dependents'])
        
        # Numeric fields
        numeric_fields = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Credit_History']
        for field in numeric_fields:
            if field in data:
                try:
                    sanitized[field] = float(data[field])
                except (ValueError, TypeError):
                    sanitized[field] = data[field]
        
        return sanitized

