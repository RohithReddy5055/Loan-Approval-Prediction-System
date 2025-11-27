""
WSGI config for Loan Approval Prediction System.
"""

from app import app, load_model

if __name__ == "__main__":
    # Load the ML model when starting the application
    load_model()
    
    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
