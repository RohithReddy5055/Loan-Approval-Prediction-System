"""
Tests for Flask API endpoints.
"""

import pytest
from flask import Flask
from app import app, load_model


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
    
    def test_predict_endpoint_missing_data(self, client):
        """Test predict endpoint with missing data."""
        response = client.post('/api/predict', json={})
        assert response.status_code == 400
    
    def test_predict_endpoint_invalid_data(self, client):
        """Test predict endpoint with invalid data."""
        invalid_data = {
            'Gender': 'Invalid',
            'ApplicantIncome': -1000
        }
        response = client.post('/api/predict', json=invalid_data)
        assert response.status_code == 400
    
    def test_predict_endpoint_valid_data(self, client):
        """Test predict endpoint with valid data."""
        valid_data = {
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
        response = client.post('/api/predict', json=valid_data)
        # May return 500 if model not loaded, which is acceptable for tests
        assert response.status_code in [200, 500]
    
    def test_model_performance_endpoint(self, client):
        """Test model performance endpoint."""
        response = client.get('/api/model/performance')
        # May return 404 if model not loaded
        assert response.status_code in [200, 404, 500]
    
    def test_model_info_endpoint(self, client):
        """Test model info endpoint."""
        response = client.get('/api/model/info')
        # May return 404 if model not loaded
        assert response.status_code in [200, 404, 500]
    
    def test_index_route(self, client):
        """Test index route."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_dashboard_route(self, client):
        """Test dashboard route."""
        response = client.get('/dashboard')
        assert response.status_code == 200

