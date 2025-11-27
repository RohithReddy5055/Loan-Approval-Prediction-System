"""
Data schemas for different loan types.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid


@dataclass
class EducationLoanApplication:
    """Schema for Education Loan Application."""
    # Applicant Details
    full_name: str
    age: int
    gender: str
    phone_number: str
    email: str
    
    # Academic Details
    course_name: str
    course_duration: int  # in years
    institution_name: str
    institution_type: str  # Government / Private / Abroad
    
    # Financial Details
    applicant_annual_income: float
    parent_guardian_income: float
    co_borrower_name: str
    co_borrower_occupation: str
    co_borrower_annual_income: float
    existing_loan: str  # Yes/No
    
    # Loan Details
    loan_amount_required: float
    repayment_period: int  # in years
    purpose: str  # Tuition / Hostel / Books / Abroad etc.
    
    # Optional Fields
    admission_proof_filename: Optional[str] = None
    
    # Metadata
    application_id: Optional[str] = None
    loan_type: str = "education"
    submitted_at: Optional[str] = None
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.application_id is None:
            data['application_id'] = str(uuid.uuid4())
        if self.submitted_at is None:
            data['submitted_at'] = datetime.now().isoformat()
        return data


@dataclass
class HomeLoanApplication:
    """Schema for Home Loan Application."""
    # Personal Details
    full_name: str
    age: int
    gender: str
    marital_status: str
    phone_number: str
    email: str
    
    # Employment Details
    employment_type: str  # Salaried / Self-Employed
    company_business_name: str
    work_experience: float  # in years
    annual_income: float
    
    # Property Details
    property_type: str  # Flat / House / Plot
    property_location: str
    property_value: float
    ownership_type: str  # New / Resale / Under Construction
    
    # Financial Details
    down_payment_amount: float
    co_applicant_income: float
    existing_emi: str  # Yes/No
    
    # Loan Details
    loan_amount_required: float
    loan_tenure: int  # in years
    
    # Optional Fields
    builder_name: Optional[str] = None
    credit_score: Optional[int] = None
    bank_statement_filename: Optional[str] = None
    itr_filename: Optional[str] = None
    
    # Metadata
    application_id: Optional[str] = None
    loan_type: str = "home"
    submitted_at: Optional[str] = None
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.application_id is None:
            data['application_id'] = str(uuid.uuid4())
        if self.submitted_at is None:
            data['submitted_at'] = datetime.now().isoformat()
        return data


@dataclass
class CarLoanApplication:
    """Schema for Car Loan Application."""
    # Personal Details
    full_name: str
    age: int
    gender: str
    phone_number: str
    email: str
    
    # Income & Employment
    employment_type: str
    work_experience: float  # in years
    
    # Vehicle Details
    car_type: str  # New / Used
    brand: str
    model: str
    car_price: float
    registration_city: str
    
    # Loan Details
    loan_amount_required: float
    loan_tenure: int  # in months
    down_payment: float
    
    # Additional
    existing_loans: str  # Yes/No
    
    # Optional Fields
    monthly_income: Optional[float] = None
    annual_income: Optional[float] = None
    credit_score: Optional[int] = None
    
    # Metadata
    application_id: Optional[str] = None
    loan_type: str = "car"
    submitted_at: Optional[str] = None
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.application_id is None:
            data['application_id'] = str(uuid.uuid4())
        if self.submitted_at is None:
            data['submitted_at'] = datetime.now().isoformat()
        return data


@dataclass
class PersonalLoanApplication:
    """Schema for Personal Loan Application."""
    # Personal Details
    full_name: str
    date_of_birth: str  # YYYY-MM-DD format
    gender: str
    phone: str
    email: str
    
    # Employment & Finance
    employment_type: str
    monthly_income: float
    work_experience: float  # in years
    existing_emi: str  # Yes/No
    
    # Loan Details
    loan_amount_required: float
    loan_tenure: int  # in months
    loan_purpose: str
    
    # Optional Fields
    credit_score: Optional[int] = None
    
    # Metadata
    application_id: Optional[str] = None
    loan_type: str = "personal"
    submitted_at: Optional[str] = None
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.application_id is None:
            data['application_id'] = str(uuid.uuid4())
        if self.submitted_at is None:
            data['submitted_at'] = datetime.now().isoformat()
        return data


@dataclass
class BusinessLoanApplication:
    """Schema for Business Loan Application."""
    # Business Details
    business_name: str
    business_type: str
    business_age: float  # in years
    annual_turnover: float
    gst_number: str
    business_address: str
    
    # Owner Details
    owner_name: str
    phone_number: str
    email: str
    
    # Financials
    existing_loans: str  # Yes/No
    
    # Loan Details
    loan_amount_required: float
    loan_tenure: int  # in years
    loan_purpose: str
    
    # Optional Fields
    itr_reports_filename: Optional[str] = None
    collateral: Optional[str] = None
    credit_score: Optional[int] = None
    
    # Metadata
    application_id: Optional[str] = None
    loan_type: str = "business"
    submitted_at: Optional[str] = None
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.application_id is None:
            data['application_id'] = str(uuid.uuid4())
        if self.submitted_at is None:
            data['submitted_at'] = datetime.now().isoformat()
        return data

