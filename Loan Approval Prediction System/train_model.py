"""
Script to train and save loan approval prediction models.
Run this script after generating the dataset to train the models.
"""

import logging
from pathlib import Path
from models.loan_model import train_and_save_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    dataset_path = Path('data/loan_dataset.csv')
    output_dir = 'models/trained_models'
    
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        logger.info("Please run 'python generate_dataset.py' first to generate the dataset.")
        exit(1)
    
    logger.info("Starting model training...")
    logger.info(f"Dataset: {dataset_path}")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        trainer = train_and_save_model(
            dataset_path=str(dataset_path),
            output_dir=output_dir
        )
        
        logger.info("=" * 50)
        logger.info("Model Training Complete!")
        logger.info("=" * 50)
        logger.info(f"Best Model: {trainer.best_model_name}")
        logger.info("\nModel Performance Summary:")
        
        for model_name, metrics in trainer.model_metrics.items():
            logger.info(f"\n{model_name}:")
            logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
            logger.info(f"  Precision: {metrics['precision']:.4f}")
            logger.info(f"  Recall:    {metrics['recall']:.4f}")
            logger.info(f"  F1-Score:  {metrics['f1_score']:.4f}")
            logger.info(f"  ROC-AUC:   {metrics.get('roc_auc', 0):.4f}")
        
        logger.info(f"\nModels saved to: {output_dir}")
        logger.info("\nYou can now start the Flask application with: python app.py")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        exit(1)

