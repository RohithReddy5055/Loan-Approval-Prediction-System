"""
Script to generate a realistic loan dataset for training.
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path

def generate_loan_dataset(n_records: int = 800, output_path: str = 'data/loan_dataset.csv'):
    """
    Generate a realistic loan dataset.
    
    Args:
        n_records: Number of records to generate
        output_path: Path to save the CSV file
    """
    np.random.seed(42)
    random.seed(42)
    
    # Generate Loan IDs
    loan_ids = [f'LP{i:05d}' for i in range(1, n_records + 1)]
    
    # Generate data
    genders = ['Male', 'Female']
    married_options = ['Yes', 'No']
    dependents_options = ['0', '1', '2', '3+']
    education_options = ['Graduate', 'Not Graduate']
    self_employed_options = ['Yes', 'No']
    property_area_options = ['Urban', 'Rural', 'Semiurban']
    
    data = {
        'Loan_ID': loan_ids,
        'Gender': np.random.choice(genders, n_records, p=[0.65, 0.35]),
        'Married': np.random.choice(married_options, n_records, p=[0.7, 0.3]),
        'Dependents': np.random.choice(dependents_options, n_records, p=[0.4, 0.25, 0.2, 0.15]),
        'Education': np.random.choice(education_options, n_records, p=[0.75, 0.25]),
        'Self_Employed': np.random.choice(self_employed_options, n_records, p=[0.15, 0.85]),
        'ApplicantIncome': np.random.lognormal(mean=9.5, sigma=0.8, size=n_records).astype(int),
        'CoapplicantIncome': np.random.lognormal(mean=7.5, sigma=1.0, size=n_records).astype(int),
        'LoanAmount': np.random.lognormal(mean=7.5, sigma=0.6, size=n_records).astype(int) * 1000,
        'Loan_Amount_Term': np.random.choice([12, 24, 36, 60, 84, 120, 180, 240, 300, 360], n_records, p=[0.05, 0.05, 0.1, 0.3, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05]),
        'Credit_History': np.random.choice([0.0, 1.0], n_records, p=[0.2, 0.8]),
        'Property_Area': np.random.choice(property_area_options, n_records, p=[0.4, 0.3, 0.3])
    }
    
    df = pd.DataFrame(data)
    
    # Introduce some missing values (realistic scenario)
    missing_indices = np.random.choice(n_records, size=int(n_records * 0.05), replace=False)
    for idx in missing_indices[:int(len(missing_indices) * 0.3)]:
        df.loc[idx, 'Gender'] = np.nan
    for idx in missing_indices[int(len(missing_indices) * 0.3):int(len(missing_indices) * 0.6)]:
        df.loc[idx, 'Married'] = np.nan
    for idx in missing_indices[int(len(missing_indices) * 0.6):]:
        df.loc[idx, 'Self_Employed'] = np.nan
    
    # Generate Loan_Status based on realistic criteria
    loan_status = []
    for idx in range(n_records):
        row = df.iloc[idx]
        
        # Factors that influence approval
        credit_score = 0
        if row['Credit_History'] == 1.0:
            credit_score += 3
        if row['Education'] == 'Graduate':
            credit_score += 1
        if row['ApplicantIncome'] > 5000:
            credit_score += 1
        if row['LoanAmount'] / row['ApplicantIncome'] < 5:  # Loan to income ratio
            credit_score += 1
        if row['Property_Area'] == 'Urban':
            credit_score += 0.5
        
        # Add some randomness
        credit_score += np.random.random() * 2
        
        # Approve if credit_score >= 4
        loan_status.append('Y' if credit_score >= 4 else 'N')
    
    df['Loan_Status'] = loan_status
    
    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Generated {n_records} loan records and saved to {output_path}")
    print(f"Loan approval rate: {(df['Loan_Status'] == 'Y').sum() / len(df) * 100:.2f}%")
    
    return df

if __name__ == '__main__':
    generate_loan_dataset(n_records=800)

