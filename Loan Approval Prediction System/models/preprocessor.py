"""
Data preprocessing module for loan approval prediction.
Handles missing values, encoding, scaling, and feature engineering.
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional, Union, List, Dict
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoanPreprocessor:
    """Preprocessor for loan application data."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.label_encoders = {}
        self.is_fitted = False
        self.feature_names = None
        
    def fit(self, X: pd.DataFrame) -> 'LoanPreprocessor':
        """
        Fit the preprocessor on training data.
        
        Args:
            X: Training features DataFrame
            
        Returns:
            Self for method chaining
        """
        logger.info("Fitting preprocessor...")
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Create a copy for processing
        X_processed = X.copy()
        
        # Handle missing values in numeric columns
        numeric_cols = X_processed.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            X_processed[numeric_cols] = self.imputer.fit_transform(X_processed[numeric_cols])
        
        # Encode categorical variables
        categorical_cols = X_processed.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
            self.label_encoders[col] = le
        
        # Scale features
        X_processed_scaled = self.scaler.fit_transform(X_processed)
        
        self.is_fitted = True
        logger.info("Preprocessor fitted successfully")
        
        return self
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform data using fitted preprocessor.
        
        Args:
            X: Features DataFrame to transform
            
        Returns:
            Transformed numpy array
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        X_processed = X.copy()
        
        # Handle missing values
        numeric_cols = X_processed.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            X_processed[numeric_cols] = self.imputer.transform(X_processed[numeric_cols])
        
        # Encode categorical variables
        categorical_cols = X_processed.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                # Handle unseen categories
                X_processed[col] = X_processed[col].astype(str).apply(
                    lambda x: x if x in le.classes_ else le.classes_[0]
                )
                X_processed[col] = le.transform(X_processed[col])
        
        # Scale features
        X_processed_scaled = self.scaler.transform(X_processed)
        
        return X_processed_scaled
    
    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
    
    def _ensure_feature_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure the dataframe contains the same feature columns used during training.
        Missing columns are added with zeros and columns are reordered to match.

        Args:
            df: Input dataframe

        Returns:
            Dataframe aligned with training feature order
        """
        if not self.feature_names:
            return df

        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0

        return df[self.feature_names]

    def preprocess_single(self, data: dict) -> np.ndarray:
        """
        Preprocess a single loan application.
        
        Args:
            data: Dictionary with loan application fields
            
        Returns:
            Preprocessed numpy array
        """
        # Convert to DataFrame
        df = pd.DataFrame([data])
        df_aligned = self._ensure_feature_columns(df)
        return self.transform(df_aligned)

    def preprocess_batch(self, data: Union[pd.DataFrame, List[Dict]]) -> np.ndarray:
        """
        Preprocess a batch of loan applications.

        Args:
            data: Dataframe or list of dictionaries containing applications

        Returns:
            Preprocessed numpy array
        """
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            df = pd.DataFrame(data)

        df_aligned = self._ensure_feature_columns(df)
        return self.transform(df_aligned)
    
    def save(self, file_path: str) -> None:
        """Save preprocessor to file."""
        joblib.dump(self, file_path)
        logger.info(f"Preprocessor saved to {file_path}")
    
    @staticmethod
    def load(file_path: str) -> 'LoanPreprocessor':
        """Load preprocessor from file."""
        preprocessor = joblib.load(file_path)
        logger.info(f"Preprocessor loaded from {file_path}")
        return preprocessor


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with missing values handled
    """
    df_processed = df.copy()
    
    # Fill missing values in categorical columns with mode
    categorical_cols = df_processed.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_processed[col].isnull().sum() > 0:
            mode_value = df_processed[col].mode()[0] if len(df_processed[col].mode()) > 0 else 'Unknown'
            df_processed[col] = df_processed[col].fillna(mode_value)
    
    # Fill missing values in numeric columns with median
    numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_processed[col].isnull().sum() > 0:
            median_value = df_processed[col].median()
            df_processed[col] = df_processed[col].fillna(median_value)
    
    return df_processed


def detect_outliers(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Detect outliers using IQR method.
    
    Args:
        df: Input DataFrame
        columns: List of numeric columns to check
        
    Returns:
        DataFrame with outlier flags
    """
    df_outliers = df.copy()
    
    for col in columns:
        if col in df_outliers.columns:
            Q1 = df_outliers[col].quantile(0.25)
            Q3 = df_outliers[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            df_outliers[f'{col}_outlier'] = (
                (df_outliers[col] < lower_bound) | (df_outliers[col] > upper_bound)
            )
    
    return df_outliers

