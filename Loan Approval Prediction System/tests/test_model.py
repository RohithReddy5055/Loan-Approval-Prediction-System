"""
Tests for loan model training and prediction.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from models.loan_model import LoanModelTrainer
from utils.data_loader import load_dataset


class TestLoanModelTrainer:
    """Test cases for LoanModelTrainer."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing."""
        data = {
            'Loan_ID': [f'LP{i:05d}' for i in range(1, 101)],
            'Gender': np.random.choice(['Male', 'Female'], 100),
            'Married': np.random.choice(['Yes', 'No'], 100),
            'Dependents': np.random.choice(['0', '1', '2', '3+'], 100),
            'Education': np.random.choice(['Graduate', 'Not Graduate'], 100),
            'Self_Employed': np.random.choice(['Yes', 'No'], 100),
            'ApplicantIncome': np.random.randint(2000, 10000, 100),
            'CoapplicantIncome': np.random.randint(0, 5000, 100),
            'LoanAmount': np.random.randint(50000, 500000, 100),
            'Loan_Amount_Term': np.random.choice([12, 24, 36, 60, 120, 240, 360], 100),
            'Credit_History': np.random.choice([0.0, 1.0], 100),
            'Property_Area': np.random.choice(['Urban', 'Rural', 'Semiurban'], 100),
            'Loan_Status': np.random.choice(['Y', 'N'], 100)
        }
        return pd.DataFrame(data)
    
    def test_trainer_initialization(self):
        """Test trainer initialization."""
        trainer = LoanModelTrainer()
        assert trainer.models == {}
        assert trainer.preprocessor is None
        assert trainer.best_model is None
    
    def test_train_models(self, sample_data, tmp_path):
        """Test model training."""
        # Save sample data
        dataset_path = tmp_path / 'test_dataset.csv'
        sample_data.to_csv(dataset_path, index=False)
        
        trainer = LoanModelTrainer()
        metrics = trainer.train_models(str(dataset_path), test_size=0.3)
        
        assert len(trainer.models) > 0
        assert trainer.best_model is not None
        assert trainer.best_model_name is not None
        assert 'Logistic Regression' in metrics
        assert 'accuracy' in metrics['Logistic Regression']
    
    def test_predict(self, sample_data, tmp_path):
        """Test prediction."""
        # Save sample data
        dataset_path = tmp_path / 'test_dataset.csv'
        sample_data.to_csv(dataset_path, index=False)
        
        trainer = LoanModelTrainer()
        trainer.train_models(str(dataset_path), test_size=0.3)
        
        # Test prediction
        test_data = {
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
        
        prediction, probability, feature_importance = trainer.predict(test_data)
        
        assert prediction in ['Approved', 'Rejected']
        assert 0 <= probability <= 1
        assert isinstance(feature_importance, dict)
    
    def test_predict_without_training(self):
        """Test that prediction fails without training."""
        trainer = LoanModelTrainer()
        
        test_data = {'ApplicantIncome': 5000}
        
        with pytest.raises(ValueError):
            trainer.predict(test_data)
    
    def test_save_and_load_models(self, sample_data, tmp_path):
        """Test saving and loading models."""
        dataset_path = tmp_path / 'test_dataset.csv'
        sample_data.to_csv(dataset_path, index=False)
        
        trainer = LoanModelTrainer()
        trainer.train_models(str(dataset_path), test_size=0.3)
        
        # Save models
        model_dir = tmp_path / 'models'
        trainer.save_models(str(model_dir))
        
        # Check files exist
        assert (model_dir / 'best_model.joblib').exists()
        assert (model_dir / 'preprocessor.joblib').exists()
        
        # Load models
        model, preprocessor, model_info = LoanModelTrainer.load_model(str(model_dir))
        
        assert model is not None
        assert preprocessor is not None
        assert model_info is not None
        assert 'best_model_name' in model_info

