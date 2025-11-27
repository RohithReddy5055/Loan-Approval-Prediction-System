"""
Data loading utilities for the Loan Approval Prediction System.
"""

import pandas as pd
import logging
from typing import Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load loan dataset from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing the loan data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file cannot be read
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded dataset with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


def split_features_target(df: pd.DataFrame, target_column: str = 'Loan_Status') -> Tuple[pd.DataFrame, pd.Series]:
    """
    Split dataset into features and target variable.
    
    Args:
        df: Input DataFrame
        target_column: Name of the target column
        
    Returns:
        Tuple of (features DataFrame, target Series)
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")
    
    X = df.drop(columns=[target_column, 'Loan_ID'], errors='ignore')
    y = df[target_column]
    
    return X, y


def save_dataset(df: pd.DataFrame, file_path: str) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        file_path: Path where to save the file
    """
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"Dataset saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving dataset: {str(e)}")
        raise

