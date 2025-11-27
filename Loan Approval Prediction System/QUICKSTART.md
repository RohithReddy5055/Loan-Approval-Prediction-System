# Quick Start Guide

Get your Loan Approval Prediction System up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or use the setup script:
```bash
python setup.py
```

## Step 2: Generate Sample Dataset

```bash
python generate_dataset.py
```

This creates `data/loan_dataset.csv` with 800 sample loan records.

## Step 3: Train Models

```bash
python train_model.py
```

This will:
- Load the dataset
- Train multiple ML models (Logistic Regression, Random Forest, XGBoost, SVM)
- Evaluate and compare models
- Save the best model to `models/trained_models/`

**Expected time**: 1-3 minutes depending on your system

## Step 4: Start the Application

```bash
python app.py
```

You should see:
```
Starting Loan Approval Prediction System...
Model loaded successfully
Starting server on port 5000
```

## Step 5: Use the Application

1. Open your browser: `http://localhost:5000`
2. Fill in the loan application form
3. Click "Predict Loan Approval"
4. View results with probability and key factors
5. Visit `http://localhost:5000/dashboard` for model performance metrics

## Troubleshooting

### "Model not found" error
- Make sure you've run `python train_model.py` first
- Check that `models/trained_models/best_model.joblib` exists

### "Dataset not found" error
- Run `python generate_dataset.py` to create the dataset
- Ensure `data/loan_dataset.csv` exists

### Port already in use
- Change the port in `app.py` or set `PORT` environment variable
- Or kill the process: `lsof -ti:5000 | xargs kill` (Linux/Mac)

## Example API Call

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the code structure
- Run tests: `pytest`
- Customize the models or add new features

Happy predicting! 🚀

