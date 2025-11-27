"""
Tests for data preprocessing module.
"""

import pytest
import pandas as pd
import numpy as np
from models.preprocessor import LoanPreprocessor, handle_missing_values


class TestLoanPreprocessor:
    """Test cases for LoanPreprocessor."""
    
    def test_preprocessor_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = LoanPreprocessor()
        assert preprocessor.is_fitted == False
        assert preprocessor.scaler is not None
        assert preprocessor.imputer is not None
    
    def test_fit_transform(self):
        """Test fit and transform."""
        preprocessor = LoanPreprocessor()
        
        # Create sample data
        data = {
            'Gender': ['Male', 'Female', 'Male'],
            'Married': ['Yes', 'No', 'Yes'],
            'ApplicantIncome': [5000, 6000, 7000],
            'LoanAmount': [100000, 150000, 200000]
        }
        df = pd.DataFrame(data)
        
        # Fit and transform
        X_transformed = preprocessor.fit_transform(df)
        
        assert preprocessor.is_fitted == True
        assert X_transformed.shape[0] == 3
        assert X_transformed.shape[1] == 4
    
    def test_transform_before_fit(self):
        """Test that transform fails before fitting."""
        preprocessor = LoanPreprocessor()
        df = pd.DataFrame({'col1': [1, 2, 3]})
        
        with pytest.raises(ValueError):
            preprocessor.transform(df)
    
    def test_preprocess_single(self):
        """Test preprocessing a single sample."""
        preprocessor = LoanPreprocessor()
        
        # Create training data
        train_data = {
            'Gender': ['Male', 'Female'],
            'ApplicantIncome': [5000, 6000]
        }
        train_df = pd.DataFrame(train_data)
        
        # Fit preprocessor
        preprocessor.fit(train_df)
        
        # Preprocess single sample
        single_data = {'Gender': 'Male', 'ApplicantIncome': 5500}
        result = preprocessor.preprocess_single(single_data)
        
        assert result.shape[0] == 1
        assert result.shape[1] == 2


class TestHandleMissingValues:
    """Test cases for handle_missing_values function."""
    
    def test_handle_missing_categorical(self):
        """Test handling missing values in categorical columns."""
        data = {
            'Gender': ['Male', None, 'Female'],
            'Married': ['Yes', 'No', None]
        }
        df = pd.DataFrame(data)
        
        result = handle_missing_values(df)
        
        assert result['Gender'].isnull().sum() == 0
        assert result['Married'].isnull().sum() == 0
    
    def test_handle_missing_numeric(self):
        """Test handling missing values in numeric columns."""
        data = {
            'ApplicantIncome': [5000, None, 7000],
            'LoanAmount': [100000, 150000, None]
        }
        df = pd.DataFrame(data)
        
        result = handle_missing_values(df)
        
        assert result['ApplicantIncome'].isnull().sum() == 0
        assert result['LoanAmount'].isnull().sum() == 0

