"""
Machine Learning model training and prediction for loan approval.
"""

import pandas as pd
import numpy as np
import logging
import joblib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns

from models.preprocessor import LoanPreprocessor, handle_missing_values
from utils.data_loader import load_dataset, split_features_target

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoanModelTrainer:
    """Trainer for loan approval prediction models."""
    
    def __init__(self):
        self.models = {}
        self.preprocessor = None
        self.best_model = None
        self.best_model_name = None
        self.model_metrics = {}
        self.feature_names = None
        
    def train_models(self, dataset_path: str, test_size: float = 0.2, random_state: int = 42) -> Dict:
        """
        Train multiple ML models on the loan dataset.
        
        Args:
            dataset_path: Path to the training dataset CSV
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary with model performance metrics
        """
        logger.info("Loading dataset...")
        df = load_dataset(dataset_path)
        
        # Handle missing values
        df = handle_missing_values(df)
        
        # Split features and target
        X, y = split_features_target(df)
        self.feature_names = X.columns.tolist()
        
        # Encode target variable
        y_encoded = (y == 'Y').astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )
        
        logger.info(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples")
        
        # Initialize preprocessor
        self.preprocessor = LoanPreprocessor()
        X_train_processed = self.preprocessor.fit_transform(X_train)
        X_test_processed = self.preprocessor.transform(X_test)
        
        # Define models
        models_config = {
            'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1),
            'XGBoost': XGBClassifier(random_state=random_state, eval_metric='logloss'),
            'SVM': SVC(probability=True, random_state=random_state)
        }
        
        # Train each model
        for name, model in models_config.items():
            logger.info(f"Training {name}...")
            model.fit(X_train_processed, y_train)
            self.models[name] = model
            
            # Evaluate model
            y_pred = model.predict(X_test_processed)
            y_pred_proba = model.predict_proba(X_test_processed)[:, 1]
            
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1_score': f1_score(y_test, y_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.0,
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
            
            self.model_metrics[name] = metrics
            logger.info(f"{name} - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        # Select best model based on F1 score
        best_f1 = -1
        for name, metrics in self.model_metrics.items():
            if metrics['f1_score'] > best_f1:
                best_f1 = metrics['f1_score']
                self.best_model_name = name
                self.best_model = self.models[name]
        
        logger.info(f"Best model: {self.best_model_name} (F1: {best_f1:.4f})")
        
        return self.model_metrics
    
    def predict(self, data: Dict) -> Tuple[str, float, Dict]:
        """
        Predict loan approval for a single application.
        
        Args:
            data: Dictionary with loan application fields
            
        Returns:
            Tuple of (prediction, probability, feature_importance)
        """
        if self.best_model is None or self.preprocessor is None:
            raise ValueError("Model not trained. Call train_models() first.")
        
        # Preprocess input
        X_processed = self.preprocessor.preprocess_single(data)
        
        # Predict
        prediction_proba = self.best_model.predict_proba(X_processed)[0]
        prediction = self.best_model.predict(X_processed)[0]
        
        # Get feature importance if available
        feature_importance = {}
        if hasattr(self.best_model, 'feature_importances_'):
            importances = self.best_model.feature_importances_
            feature_importance = dict(zip(self.feature_names, importances))
            # Sort by importance
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        # Convert prediction
        prediction_label = 'Approved' if prediction == 1 else 'Rejected'
        probability = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
        
        return prediction_label, float(probability), feature_importance
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the best model."""
        if self.best_model is None:
            raise ValueError("Model not trained.")
        
        if not hasattr(self.best_model, 'feature_importances_'):
            return {}
        
        importances = self.best_model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importances))
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    def save_models(self, directory: str = 'models/trained_models') -> None:
        """Save all trained models and preprocessor."""
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Save preprocessor
        preprocessor_path = Path(directory) / 'preprocessor.joblib'
        self.preprocessor.save(str(preprocessor_path))
        
        # Save models
        for name, model in self.models.items():
            model_path = Path(directory) / f'{name.lower().replace(" ", "_")}.joblib'
            joblib.dump(model, model_path)
            logger.info(f"Saved {name} to {model_path}")
        
        # Save best model separately
        if self.best_model:
            best_model_path = Path(directory) / 'best_model.joblib'
            joblib.dump(self.best_model, best_model_path)
            logger.info(f"Saved best model ({self.best_model_name}) to {best_model_path}")
        
        # Save model info
        model_info = {
            'best_model_name': self.best_model_name,
            'metrics': self.model_metrics,
            'feature_names': self.feature_names
        }
        info_path = Path(directory) / 'model_info.joblib'
        joblib.dump(model_info, info_path)
        logger.info(f"Saved model info to {info_path}")
    
    @staticmethod
    def load_model(directory: str = 'models/trained_models') -> Tuple[object, LoanPreprocessor, Dict]:
        """
        Load trained model and preprocessor.
        
        Returns:
            Tuple of (model, preprocessor, model_info)
        """
        directory_path = Path(directory)
        
        # Load preprocessor
        preprocessor_path = directory_path / 'preprocessor.joblib'
        preprocessor = LoanPreprocessor.load(str(preprocessor_path))
        
        # Load model info
        info_path = directory_path / 'model_info.joblib'
        model_info = joblib.load(info_path)
        
        # Load best model
        best_model_path = directory_path / 'best_model.joblib'
        model = joblib.load(best_model_path)
        
        logger.info(f"Loaded model: {model_info['best_model_name']}")
        
        return model, preprocessor, model_info


def train_and_save_model(dataset_path: str = 'data/loan_dataset.csv', 
                         output_dir: str = 'models/trained_models') -> LoanModelTrainer:
    """
    Convenience function to train and save models.
    
    Args:
        dataset_path: Path to dataset
        output_dir: Directory to save models
        
    Returns:
        Trained LoanModelTrainer instance
    """
    trainer = LoanModelTrainer()
    trainer.train_models(dataset_path)
    trainer.save_models(output_dir)
    return trainer

