"""
Validators for different loan types.
"""

import re
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EducationLoanValidator:
    """Validator for Education Loan applications."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (10 digits)."""
        phone_clean = re.sub(r'[^\d]', '', phone)
        return len(phone_clean) >= 10
    
    @staticmethod
    def validate(data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate education loan application data."""
        # Required fields (non-numeric)
        required_fields = [
            'full_name', 'age', 'gender', 'phone_number', 'email',
            'course_name', 'course_duration', 'institution_name', 'institution_type',
            'co_borrower_name', 'co_borrower_occupation', 'existing_loan',
            'loan_amount_required', 'repayment_period', 'purpose'
        ]
        
        # Check non-numeric required fields
        for field in required_fields:
            if field not in data or (not isinstance(data[field], (int, float)) and not data[field]):
                return False, f"Missing required field: {field}"
        
        # Check numeric required fields (allow 0 for students who don't have income)
        numeric_required_fields = [
            'applicant_annual_income', 'parent_guardian_income', 'co_borrower_annual_income'
        ]
        
        for field in numeric_required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
            # Allow 0 or positive numbers, but not None, empty string, or negative
            try:
                value = float(data[field])
                if value < 0:
                    return False, f"{field} cannot be negative"
            except (ValueError, TypeError):
                if data[field] is None or data[field] == '':
                    return False, f"Missing required field: {field}"
        
        # Validate age
        try:
            age = int(data['age'])
            if age < 16 or age > 65:
                return False, "Age must be between 16 and 65"
        except (ValueError, TypeError):
            return False, "Invalid age"
        
        # Validate email
        if not EducationLoanValidator.validate_email(data['email']):
            return False, "Invalid email format"
        
        # Validate phone
        if not EducationLoanValidator.validate_phone(data['phone_number']):
            return False, "Invalid phone number"
        
        # Validate gender
        if data['gender'] not in ['Male', 'Female', 'Other']:
            return False, "Invalid gender"
        
        # Validate institution_type
        if data['institution_type'] not in ['Government', 'Private', 'Abroad']:
            return False, "Invalid institution type"
        
        # Validate existing_loan
        if data['existing_loan'] not in ['Yes', 'No']:
            return False, "Invalid existing_loan value (must be Yes or No)"
        
        # Validate numeric fields
        numeric_fields = {
            'course_duration': (1, 10),
            'applicant_annual_income': (0, 10000000),  # Allow 0 for students
            'parent_guardian_income': (0, 10000000),
            'co_borrower_annual_income': (0, 10000000),
            'loan_amount_required': (10000, 5000000),
            'repayment_period': (1, 20)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            try:
                value = float(data[field])
                # Special case: allow 0 for applicant_annual_income (students may have no income)
                if field == 'applicant_annual_income' and value == 0:
                    continue  # Skip validation for 0 income
                if value < min_val or value > max_val:
                    return False, f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Invalid {field}"
        
        return True, None


class HomeLoanValidator:
    """Validator for Home Loan applications."""
    
    @staticmethod
    def validate(data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate home loan application data."""
        # Check non-numeric required fields
        non_numeric_fields = [
            'full_name', 'gender', 'marital_status', 'phone_number', 'email',
            'employment_type', 'company_business_name', 'property_type',
            'property_location', 'ownership_type', 'existing_emi'
        ]
        
        for field in non_numeric_fields:
            if field not in data or (not isinstance(data[field], (int, float)) and not data[field]):
                return False, f"Missing required field: {field}"
        
        # Check numeric required fields (allow 0 for co_applicant_income)
        numeric_required_fields = ['age', 'work_experience', 'annual_income', 'property_value',
                                  'down_payment_amount', 'co_applicant_income', 'loan_amount_required', 'loan_tenure']
        
        for field in numeric_required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
            # Allow 0 or positive numbers, but not None, empty string, or negative
            try:
                value = float(data[field])
                if value < 0:
                    return False, f"{field} cannot be negative"
            except (ValueError, TypeError):
                if data[field] is None or data[field] == '':
                    return False, f"Missing required field: {field}"
        
        # Validate age
        try:
            age = int(data['age'])
            if age < 18 or age > 70:
                return False, "Age must be between 18 and 70"
        except (ValueError, TypeError):
            return False, "Invalid age"
        
        # Validate email
        if not EducationLoanValidator.validate_email(data['email']):
            return False, "Invalid email format"
        
        # Validate phone
        if not EducationLoanValidator.validate_phone(data['phone_number']):
            return False, "Invalid phone number"
        
        # Validate marital_status
        if data['marital_status'] not in ['Single', 'Married', 'Divorced', 'Widowed']:
            return False, "Invalid marital status"
        
        # Validate employment_type
        if data['employment_type'] not in ['Salaried', 'Self-Employed']:
            return False, "Invalid employment type"
        
        # Validate property_type
        if data['property_type'] not in ['Flat', 'House', 'Plot']:
            return False, "Invalid property type"
        
        # Validate ownership_type
        if data['ownership_type'] not in ['New', 'Resale', 'Under Construction']:
            return False, "Invalid ownership type"
        
        # Validate existing_emi
        if data['existing_emi'] not in ['Yes', 'No']:
            return False, "Invalid existing_emi value"
        
        # Validate numeric fields
        numeric_fields = {
            'work_experience': (0, 50),
            'annual_income': (100000, 10000000),
            'property_value': (500000, 50000000),
            'down_payment_amount': (0, 50000000),
            'co_applicant_income': (0, 10000000),
            'loan_amount_required': (500000, 50000000),
            'loan_tenure': (5, 30)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            try:
                value = float(data[field])
                if value < min_val or value > max_val:
                    return False, f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Invalid {field}"
        
        # Validate credit_score if provided
        if 'credit_score' in data and data['credit_score']:
            try:
                score = int(data['credit_score'])
                if score < 300 or score > 850:
                    return False, "Credit score must be between 300 and 850"
            except (ValueError, TypeError):
                return False, "Invalid credit score"
        
        return True, None


class CarLoanValidator:
    """Validator for Car Loan applications."""
    
    @staticmethod
    def validate(data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate car loan application data."""
        required_fields = [
            'full_name', 'age', 'gender', 'phone_number', 'email',
            'employment_type', 'work_experience',
            'car_type', 'brand', 'model', 'car_price', 'registration_city',
            'loan_amount_required', 'loan_tenure', 'down_payment', 'existing_loans'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate age
        try:
            age = int(data['age'])
            if age < 18 or age > 70:
                return False, "Age must be between 18 and 70"
        except (ValueError, TypeError):
            return False, "Invalid age"
        
        # Validate email
        if not EducationLoanValidator.validate_email(data['email']):
            return False, "Invalid email format"
        
        # Validate phone
        if not EducationLoanValidator.validate_phone(data['phone_number']):
            return False, "Invalid phone number"
        
        # Validate car_type
        if data['car_type'] not in ['New', 'Used']:
            return False, "Invalid car type"
        
        # Validate existing_loans
        if data['existing_loans'] not in ['Yes', 'No']:
            return False, "Invalid existing_loans value"
        
        # Validate income (either monthly or annual)
        has_monthly = 'monthly_income' in data and data['monthly_income']
        has_annual = 'annual_income' in data and data['annual_income']
        
        if not has_monthly and not has_annual:
            return False, "Either monthly_income or annual_income is required"
        
        # Validate numeric fields
        numeric_fields = {
            'work_experience': (0, 50),
            'car_price': (100000, 10000000),
            'loan_amount_required': (50000, 10000000),
            'loan_tenure': (12, 84),  # 1-7 years in months
            'down_payment': (0, 10000000)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            try:
                value = float(data[field])
                if value < min_val or value > max_val:
                    return False, f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Invalid {field}"
        
        return True, None


class PersonalLoanValidator:
    """Validator for Personal Loan applications."""
    
    @staticmethod
    def validate_date(date_string: str) -> bool:
        """Validate date in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate(data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate personal loan application data."""
        required_fields = [
            'full_name', 'date_of_birth', 'gender', 'phone', 'email',
            'employment_type', 'monthly_income', 'work_experience', 'existing_emi',
            'loan_amount_required', 'loan_tenure', 'loan_purpose'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate date_of_birth
        if not PersonalLoanValidator.validate_date(data['date_of_birth']):
            return False, "Invalid date_of_birth format (must be YYYY-MM-DD)"
        
        # Validate email
        if not EducationLoanValidator.validate_email(data['email']):
            return False, "Invalid email format"
        
        # Validate phone
        if not EducationLoanValidator.validate_phone(data['phone']):
            return False, "Invalid phone number"
        
        # Validate gender
        if data['gender'] not in ['Male', 'Female', 'Other']:
            return False, "Invalid gender"
        
        # Validate employment_type
        if data['employment_type'] not in ['Salaried', 'Self-Employed', 'Business']:
            return False, "Invalid employment type"
        
        # Validate existing_emi
        if data['existing_emi'] not in ['Yes', 'No']:
            return False, "Invalid existing_emi value"
        
        # Validate numeric fields
        numeric_fields = {
            'monthly_income': (10000, 5000000),
            'work_experience': (0, 50),
            'loan_amount_required': (10000, 5000000),
            'loan_tenure': (6, 60)  # months
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            try:
                value = float(data[field])
                if value < min_val or value > max_val:
                    return False, f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Invalid {field}"
        
        # Validate credit_score if provided
        if 'credit_score' in data and data['credit_score']:
            try:
                score = int(data['credit_score'])
                if score < 300 or score > 850:
                    return False, "Credit score must be between 300 and 850"
            except (ValueError, TypeError):
                return False, "Invalid credit score"
        
        return True, None


class BusinessLoanValidator:
    """Validator for Business Loan applications."""
    
    @staticmethod
    def validate_gst(gst_number: str) -> bool:
        """Validate GST number format (15 characters, with or without hyphens)."""
        if not gst_number:
            return False
        
        # Remove hyphens and spaces, then check length
        cleaned_gst = gst_number.replace('-', '').replace(' ', '').strip().upper()
        
        # Must be exactly 15 alphanumeric characters
        if len(cleaned_gst) != 15:
            return False
        
        # Check if all characters are alphanumeric
        if not cleaned_gst.isalnum():
            return False
        
        return True
    
    @staticmethod
    def validate(data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate business loan application data."""
        required_fields = [
            'business_name', 'business_type', 'business_age', 'annual_turnover',
            'gst_number', 'business_address',
            'owner_name', 'phone_number', 'email',
            'existing_loans', 'credit_score', 'loan_amount_required', 'loan_tenure', 'loan_purpose'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate email
        if not EducationLoanValidator.validate_email(data['email']):
            return False, "Invalid email format"
        
        # Validate phone
        if not EducationLoanValidator.validate_phone(data['phone_number']):
            return False, "Invalid phone number"
        
        # Validate GST number
        if not BusinessLoanValidator.validate_gst(data['gst_number']):
            return False, "Invalid GST number format (must be 15 characters)"
        
        # Validate existing_loans
        if data['existing_loans'] not in ['Yes', 'No']:
            return False, "Invalid existing_loans value"
        
        # Validate credit_score
        if 'credit_score' in data and data['credit_score']:
            try:
                score = int(data['credit_score'])
                if score < 300 or score > 900:
                    return False, "Credit score must be between 300 and 900"
            except (ValueError, TypeError):
                return False, "Invalid credit score"
        
        # Validate numeric fields
        numeric_fields = {
            'business_age': (0, 100),
            'annual_turnover': (100000, 100000000),
            'loan_amount_required': (100000, 50000000),
            'loan_tenure': (1, 10)  # years
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            try:
                value = float(data[field])
                if value < min_val or value > max_val:
                    return False, f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Invalid {field}"
        
        return True, None

