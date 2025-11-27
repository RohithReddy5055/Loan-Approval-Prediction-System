# Loan Approval Prediction System

A comprehensive machine learning-based web application for predicting loan approval decisions. The system uses multiple ML algorithms to analyze loan applications and provides predictions with detailed insights.

## Features

- **Multiple ML Models**: Logistic Regression, Random Forest, XGBoost, and SVM
- **Web Interface**: Modern, responsive UI for loan application submission
- **Real-time Predictions**: Get instant loan approval/rejection predictions
- **Model Dashboard**: Visualize model performance metrics and feature importance
- **Data Visualization**: Interactive charts and graphs for model analysis
- **RESTful API**: Complete backend API for predictions and model information

## Project Structure

```
Loan Approval Prediction System/
├── app.py                      # Main Flask application
├── generate_dataset.py         # Script to generate sample dataset
├── models/
│   ├── loan_model.py          # Model training and prediction
│   ├── preprocessor.py        # Data preprocessing
│   └── trained_models/        # Saved model files
├── data/
│   └── loan_dataset.csv       # Training dataset
├── templates/
│   ├── index.html             # Main prediction page
│   └── dashboard.html         # Model performance dashboard
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling
│   └── js/
│       ├── main.js            # Frontend logic
│       └── dashboard.js       # Dashboard visualizations
├── utils/
│   ├── data_loader.py         # Data loading utilities
│   └── validators.py          # Input validation
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate sample dataset**
   ```bash
   python generate_dataset.py
   ```
   This will create `data/loan_dataset.csv` with 800 sample records.

5. **Train the models**
   ```bash
   python -c "from models.loan_model import train_and_save_model; train_and_save_model()"
   ```
   Or create a training script:
   ```python
   from models.loan_model import train_and_save_model
   train_and_save_model()
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - Use the form to submit loan applications
   - Visit `/dashboard` to view model performance metrics

## Usage

### Making Predictions

1. Navigate to the home page (`http://localhost:5000`)
2. Fill in the loan application form with the following details:
   - Gender (Male/Female)
   - Married status (Yes/No)
   - Number of Dependents (0, 1, 2, 3+)
   - Education level (Graduate/Not Graduate)
   - Self-employed status (Yes/No)
   - Applicant Income (in ₹)
   - Co-applicant Income (in ₹)
   - Loan Amount (in ₹)
   - Loan Term (in months)
   - Credit History (1.0 for good, 0.0 for bad)
   - Property Area (Urban/Rural/Semiurban)

3. Click "Predict Loan Approval"
4. View the prediction result with probability and key factors

### API Endpoints

#### POST `/api/predict`
Submit a loan application and get prediction.

**Request Body:**
```json
{
  "Gender": "Male",
  "Married": "Yes",
  "Dependents": "0",
  "Education": "Graduate",
  "Self_Employed": "No",
  "ApplicantIncome": 5000,
  "CoapplicantIncome": 2000,
  "LoanAmount": 150000,
  "Loan_Amount_Term": 360,
  "Credit_History": 1.0,
  "Property_Area": "Urban"
}
```

**Response:**
```json
{
  "prediction": "Approved",
  "probability": 85.5,
  "status": "approved",
  "feature_importance": {
    "Credit_History": 0.35,
    "ApplicantIncome": 0.25,
    ...
  }
}
```

#### GET `/api/model/performance`
Get model performance metrics for all trained models.

#### GET `/api/model/info`
Get model information and feature importance.

#### GET `/api/health`
Health check endpoint.

## Model Training

The system trains multiple models and automatically selects the best one based on F1 score. Models are saved in `models/trained_models/` directory.

### Training Script Example

```python
from models.loan_model import train_and_save_model

# Train models with default dataset
trainer = train_and_save_model(
    dataset_path='data/loan_dataset.csv',
    output_dir='models/trained_models'
)

# Access metrics
print(f"Best model: {trainer.best_model_name}")
print(f"Metrics: {trainer.model_metrics}")
```

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_model.py
```

## Configuration

### Environment Variables

Create a `.env` file (see `.env.example`) with:

```
PORT=5000
FLASK_DEBUG=False
```

## Technologies Used

- **Backend**: Flask, Python
- **Machine Learning**: scikit-learn, XGBoost, pandas, numpy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Visualization**: Chart.js, matplotlib, seaborn
- **Testing**: pytest

## Model Performance

The system evaluates models using:
- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC Score
- Confusion Matrix

Models typically achieve >75% accuracy on the test set.

## Data Preprocessing

The preprocessing pipeline includes:
- Missing value imputation (median for numeric, mode for categorical)
- Label encoding for categorical variables
- Feature scaling using StandardScaler
- Outlier detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is open source and available for educational purposes.

## Troubleshooting

### Model not found error
- Ensure you've run the dataset generation script
- Train the models before starting the application
- Check that `models/trained_models/` directory contains model files

### Port already in use
- Change the port in `.env` file or modify `app.py`
- Kill the process using the port: `lsof -ti:5000 | xargs kill` (Linux/Mac)

### Import errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Future Enhancements

- [ ] Model retraining interface
- [ ] Prediction history/logging
- [ ] User authentication
- [ ] Database integration
- [ ] Docker containerization
- [ ] Deployment scripts

## Contact

For questions or issues, please open an issue on the project repository.

---

**Note**: This is a demonstration project. For production use, additional security measures, error handling, and validation should be implemented.
