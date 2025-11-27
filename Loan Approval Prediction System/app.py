"""
Flask application for Loan Approval Prediction System.
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import traceback
import pandas as pd

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from models.loan_model import LoanModelTrainer
from utils.validators import LoanApplicationValidator
from utils.loan_schemas import (
    EducationLoanApplication, HomeLoanApplication, CarLoanApplication,
    PersonalLoanApplication, BusinessLoanApplication
)
from utils.loan_validators import (
    EducationLoanValidator, HomeLoanValidator, CarLoanValidator,
    PersonalLoanValidator, BusinessLoanValidator
)
from utils.loan_storage import save_application, get_all_applications, get_applications_by_type, get_application_by_id, update_application_status, delete_application
from utils.emi_calculator import calculate_emi_for_loan_type, get_loan_details
from utils.email_service import email_service
from utils.approval_engine import check_loan_approval

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Enable better error reporting
app.config['PROPAGATE_EXCEPTIONS'] = True

# Global variables for model
model_trainer = None
model = None
preprocessor = None
model_info = None


def load_model():
    """Load the trained model and preprocessor."""
    global model, preprocessor, model_info, model_trainer
    
    try:
        model_dir = Path('models/trained_models')
        if not (model_dir / 'best_model.joblib').exists():
            logger.warning("Trained model not found. Training new model...")
            # Train model if not exists
            dataset_path = Path('data/loan_dataset.csv')
            if dataset_path.exists():
                model_trainer = LoanModelTrainer()
                model_trainer.train_models(str(dataset_path))
                model_trainer.save_models()
                model = model_trainer.best_model
                preprocessor = model_trainer.preprocessor
                model_info = {
                    'best_model_name': model_trainer.best_model_name,
                    'metrics': model_trainer.model_metrics,
                    'feature_names': model_trainer.feature_names
                }
            else:
                logger.error("Dataset not found. Please generate dataset first.")
                return False
        else:
            model, preprocessor, model_info = LoanModelTrainer.load_model()
            logger.info("Model loaded successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.error(traceback.format_exc())
        return False


@app.route('/')
def index():
    """Render the home page with loan type selection."""
    return render_template('home.html')


@app.route('/apply/education-loan')
def education_loan_form():
    """Render education loan application form."""
    return render_template('loans/education_loan.html')


@app.route('/apply/home-loan')
def home_loan_form():
    """Render home loan application form."""
    try:
        return render_template('loans/home_loan.html')
    except Exception as e:
        logger.error(f"Error rendering home loan form: {e}")
        # Return a simple message if template doesn't exist
        return f"""
        <html>
        <head><title>Home Loan Application</title></head>
        <body>
            <h1>Home Loan Application Form</h1>
            <p>Form template not found. Please create templates/loans/home_loan.html</p>
            <p>Error: {str(e)}</p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """, 200


@app.route('/apply/car-loan')
def car_loan_form():
    """Render car loan application form."""
    try:
        return render_template('loans/car_loan.html')
    except Exception as e:
        logger.error(f"Error rendering car loan form: {e}")
        return f"""
        <html>
        <head><title>Car Loan Application</title></head>
        <body>
            <h1>Car Loan Application Form</h1>
            <p>Form template not found. Please create templates/loans/car_loan.html</p>
            <p>Error: {str(e)}</p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """, 200


@app.route('/apply/personal-loan')
def personal_loan_form():
    """Render personal loan application form."""
    try:
        return render_template('loans/personal_loan.html')
    except Exception as e:
        logger.error(f"Error rendering personal loan form: {e}")
        return f"""
        <html>
        <head><title>Personal Loan Application</title></head>
        <body>
            <h1>Personal Loan Application Form</h1>
            <p>Form template not found. Please create templates/loans/personal_loan.html</p>
            <p>Error: {str(e)}</p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """, 200


@app.route('/apply/business-loan')
def business_loan_form():
    """Render business loan application form."""
    try:
        return render_template('loans/business_loan.html')
    except Exception as e:
        logger.error(f"Error rendering business loan form: {e}")
        return f"""
        <html>
        <head><title>Business Loan Application</title></head>
        <body>
            <h1>Business Loan Application Form</h1>
            <p>Form template not found. Please create templates/loans/business_loan.html</p>
            <p>Error: {str(e)}</p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """, 200


@app.route('/admin')
def admin_panel():
    """Render admin panel to view all applications."""
    return render_template('admin.html')


@app.route('/dashboard')
def dashboard():
    """Render the model performance dashboard."""
    return render_template('dashboard.html')


@app.route('/api/apply/education-loan', methods=['POST'])
def apply_education_loan():
    """Handle education loan application submission."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate
        validator = EducationLoanValidator()
        is_valid, error_message = validator.validate(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create application object
        try:
            application = EducationLoanApplication(**data)
            application_dict = application.to_dict()
        except Exception as schema_error:
            logger.error(f"Error creating application object: {schema_error}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Invalid application data: {str(schema_error)}'}), 400
        
        # Calculate EMI
        try:
            emi_info = calculate_emi_for_loan_type(
                'education',
                application.loan_amount_required,
                application.repayment_period,
                'years'
            )
            application_dict['emi_info'] = emi_info
        except Exception as emi_error:
            logger.warning(f"EMI calculation failed: {emi_error}, continuing without EMI info")
            application_dict['emi_info'] = None
        
        # Check approval using rules engine
        approval_result = check_loan_approval('education', application_dict)
        if approval_result['approved']:
            application_dict['status'] = 'approved'
            application_dict['approval_reason'] = approval_result['reason']
        else:
            application_dict['status'] = 'rejected'
            application_dict['rejection_reason'] = approval_result['reason']
        
        # Save application
        save_result = save_application(application_dict)
        if save_result:
            # Send confirmation email
            try:
                email_service.send_application_confirmation(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='education',
                    loan_amount=application.loan_amount_required,
                    emi_info=emi_info
                )
            except Exception as email_error:
                logger.warning(f"Failed to send confirmation email: {email_error}")
            
            # Send status update email (approved/rejected) with reason
            try:
                logger.info(f"Sending status update email for application {application_dict['application_id']} - Status: {application_dict['status']}")
                email_sent = email_service.send_status_update(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='education',
                    status=application_dict['status'],
                    approval_reason=approval_result['reason']
                )
                if email_sent:
                    logger.info(f"Status update email sent successfully to {application.email}")
                else:
                    logger.warning(f"Status update email failed to send to {application.email}")
            except Exception as email_error:
                logger.error(f"Failed to send status update email: {email_error}")
                logger.error(traceback.format_exc())
            
            return jsonify({
                'success': True,
                'message': 'Education loan application submitted successfully',
                'application_id': application_dict['application_id'],
                'emi_info': emi_info,
                'approval_status': application_dict['status'],
                'approval_reason': approval_result['reason']
            }), 201
        else:
            logger.error(f"Failed to save application: {application_dict.get('application_id', 'unknown')}")
            return jsonify({
                'error': 'Failed to save application. Please check server logs for details.',
                'debug': 'Check if data/applications directory is writable'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in education loan application: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Application failed: {str(e)}'}), 500


@app.route('/api/apply/home-loan', methods=['POST'])
def apply_home_loan():
    """Handle home loan application submission."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate
        validator = HomeLoanValidator()
        is_valid, error_message = validator.validate(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create application object
        try:
            application = HomeLoanApplication(**data)
            application_dict = application.to_dict()
        except Exception as schema_error:
            logger.error(f"Error creating home loan application object: {schema_error}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Invalid application data: {str(schema_error)}'}), 400
        
        # Calculate EMI
        emi_info = None
        try:
            emi_info = calculate_emi_for_loan_type(
                'home',
                application.loan_amount_required,
                application.loan_tenure,
                'years'
            )
            application_dict['emi_info'] = emi_info
        except Exception as emi_error:
            logger.warning(f"EMI calculation failed: {emi_error}, continuing without EMI info")
            application_dict['emi_info'] = None
        
        # Check approval using rules engine
        approval_result = check_loan_approval('home', application_dict)
        if approval_result['approved']:
            application_dict['status'] = 'approved'
            application_dict['approval_reason'] = approval_result['reason']
        else:
            application_dict['status'] = 'rejected'
            application_dict['rejection_reason'] = approval_result['reason']
        
        # Save application
        save_result = save_application(application_dict)
        if save_result:
            # Send confirmation email
            try:
                email_service.send_application_confirmation(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='home',
                    loan_amount=application.loan_amount_required,
                    emi_info=emi_info
                )
            except Exception as email_error:
                logger.warning(f"Failed to send confirmation email: {email_error}")
            
            # Send status update email (approved/rejected) with reason
            try:
                logger.info(f"Sending status update email for application {application_dict['application_id']} - Status: {application_dict['status']}")
                email_sent = email_service.send_status_update(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='home',
                    status=application_dict['status'],
                    approval_reason=approval_result['reason']
                )
                if email_sent:
                    logger.info(f"Status update email sent successfully to {application.email}")
                else:
                    logger.warning(f"Status update email failed to send to {application.email}")
            except Exception as email_error:
                logger.error(f"Failed to send status update email: {email_error}")
                logger.error(traceback.format_exc())
            
            return jsonify({
                'success': True,
                'message': 'Home loan application submitted successfully',
                'application_id': application_dict['application_id'],
                'emi_info': emi_info if emi_info else None,
                'approval_status': application_dict['status'],
                'approval_reason': approval_result['reason']
            }), 201
        else:
            logger.error(f"Failed to save home loan application: {application_dict.get('application_id', 'unknown')}")
            return jsonify({
                'error': 'Failed to save application. Please check server logs for details.'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in home loan application: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Application failed: {str(e)}'}), 500


@app.route('/api/apply/car-loan', methods=['POST'])
def apply_car_loan():
    """Handle car loan application submission."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate
        validator = CarLoanValidator()
        is_valid, error_message = validator.validate(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create application object
        application = CarLoanApplication(**data)
        application_dict = application.to_dict()
        
        # Calculate EMI
        emi_info = calculate_emi_for_loan_type(
            'car',
            application.loan_amount_required,
            application.loan_tenure,
            'months'
        )
        application_dict['emi_info'] = emi_info
        
        # Check approval using rules engine
        approval_result = check_loan_approval('car', application_dict)
        if approval_result['approved']:
            application_dict['status'] = 'approved'
            application_dict['approval_reason'] = approval_result['reason']
        else:
            application_dict['status'] = 'rejected'
            application_dict['rejection_reason'] = approval_result['reason']
        
        # Save application
        if save_application(application_dict):
            # Send confirmation email
            try:
                email_service.send_application_confirmation(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='car',
                    loan_amount=application.loan_amount_required,
                    emi_info=emi_info
                )
            except Exception as email_error:
                logger.warning(f"Failed to send confirmation email: {email_error}")
            
            # Send status update email (approved/rejected) with reason
            try:
                logger.info(f"Sending status update email for application {application_dict['application_id']} - Status: {application_dict['status']}")
                email_sent = email_service.send_status_update(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='car',
                    status=application_dict['status'],
                    approval_reason=approval_result['reason']
                )
                if email_sent:
                    logger.info(f"Status update email sent successfully to {application.email}")
                else:
                    logger.warning(f"Status update email failed to send to {application.email}")
            except Exception as email_error:
                logger.error(f"Failed to send status update email: {email_error}")
                logger.error(traceback.format_exc())
            
            return jsonify({
                'success': True,
                'message': 'Car loan application submitted successfully',
                'application_id': application_dict['application_id'],
                'emi_info': emi_info,
                'approval_status': application_dict['status'],
                'approval_reason': approval_result['reason']
            }), 201
        else:
            return jsonify({'error': 'Failed to save application'}), 500
            
    except Exception as e:
        logger.error(f"Error in car loan application: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Application failed: {str(e)}'}), 500


@app.route('/api/apply/personal-loan', methods=['POST'])
def apply_personal_loan():
    """Handle personal loan application submission."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate
        validator = PersonalLoanValidator()
        is_valid, error_message = validator.validate(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create application object
        application = PersonalLoanApplication(**data)
        application_dict = application.to_dict()
        
        # Calculate EMI
        emi_info = calculate_emi_for_loan_type(
            'personal',
            application.loan_amount_required,
            application.loan_tenure,
            'months'
        )
        application_dict['emi_info'] = emi_info
        
        # Check approval using rules engine
        approval_result = check_loan_approval('personal', application_dict)
        if approval_result['approved']:
            application_dict['status'] = 'approved'
            application_dict['approval_reason'] = approval_result['reason']
        else:
            application_dict['status'] = 'rejected'
            application_dict['rejection_reason'] = approval_result['reason']
        
        # Save application
        if save_application(application_dict):
            # Send confirmation email
            try:
                email_service.send_application_confirmation(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='personal',
                    loan_amount=application.loan_amount_required,
                    emi_info=emi_info
                )
            except Exception as email_error:
                logger.warning(f"Failed to send confirmation email: {email_error}")
            
            # Send status update email (approved/rejected) with reason
            try:
                logger.info(f"Sending status update email for application {application_dict['application_id']} - Status: {application_dict['status']}")
                email_sent = email_service.send_status_update(
                    to_email=application.email,
                    applicant_name=application.full_name,
                    application_id=application_dict['application_id'],
                    loan_type='personal',
                    status=application_dict['status'],
                    approval_reason=approval_result['reason']
                )
                if email_sent:
                    logger.info(f"Status update email sent successfully to {application.email}")
                else:
                    logger.warning(f"Status update email failed to send to {application.email}")
            except Exception as email_error:
                logger.error(f"Failed to send status update email: {email_error}")
                logger.error(traceback.format_exc())
            
            return jsonify({
                'success': True,
                'message': 'Personal loan application submitted successfully',
                'application_id': application_dict['application_id'],
                'emi_info': emi_info,
                'approval_status': application_dict['status'],
                'approval_reason': approval_result['reason']
            }), 201
        else:
            return jsonify({'error': 'Failed to save application'}), 500
            
    except Exception as e:
        logger.error(f"Error in personal loan application: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Application failed: {str(e)}'}), 500


@app.route('/api/apply/business-loan', methods=['POST'])
def apply_business_loan():
    """Handle business loan application submission."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate
        validator = BusinessLoanValidator()
        is_valid, error_message = validator.validate(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create application object
        application = BusinessLoanApplication(**data)
        application_dict = application.to_dict()
        
        # Calculate EMI
        emi_info = calculate_emi_for_loan_type(
            'business',
            application.loan_amount_required,
            application.loan_tenure,
            'years'
        )
        application_dict['emi_info'] = emi_info
        
        # Check approval using rules engine
        approval_result = check_loan_approval('business', application_dict)
        if approval_result['approved']:
            application_dict['status'] = 'approved'
            application_dict['approval_reason'] = approval_result['reason']
        else:
            application_dict['status'] = 'rejected'
            application_dict['rejection_reason'] = approval_result['reason']
        
        # Save application
        if save_application(application_dict):
            # Send confirmation email
            try:
                email_service.send_application_confirmation(
                    to_email=application.email,
                    applicant_name=application.owner_name,
                    application_id=application_dict['application_id'],
                    loan_type='business',
                    loan_amount=application.loan_amount_required,
                    emi_info=emi_info
                )
            except Exception as email_error:
                logger.warning(f"Failed to send confirmation email: {email_error}")
            
            # Send status update email (approved/rejected) with reason
            try:
                logger.info(f"Sending status update email for application {application_dict['application_id']} - Status: {application_dict['status']}")
                email_sent = email_service.send_status_update(
                    to_email=application.email,
                    applicant_name=application.owner_name,
                    application_id=application_dict['application_id'],
                    loan_type='business',
                    status=application_dict['status'],
                    approval_reason=approval_result['reason']
                )
                if email_sent:
                    logger.info(f"Status update email sent successfully to {application.email}")
                else:
                    logger.warning(f"Status update email failed to send to {application.email}")
            except Exception as email_error:
                logger.error(f"Failed to send status update email: {email_error}")
                logger.error(traceback.format_exc())
            
            return jsonify({
                'success': True,
                'message': 'Business loan application submitted successfully',
                'application_id': application_dict['application_id'],
                'emi_info': emi_info,
                'approval_status': application_dict['status'],
                'approval_reason': approval_result['reason']
            }), 201
        else:
            return jsonify({'error': 'Failed to save application'}), 500
            
    except Exception as e:
        logger.error(f"Error in business loan application: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Application failed: {str(e)}'}), 500


@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get all applications (admin endpoint)."""
    try:
        loan_type = request.args.get('type')
        
        if loan_type:
            applications = get_applications_by_type(loan_type)
        else:
            applications = get_all_applications()
        
        return jsonify({
            'success': True,
            'count': len(applications),
            'applications': applications
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting applications: {str(e)}")
        return jsonify({'error': f'Failed to get applications: {str(e)}'}), 500


@app.route('/api/applications/<application_id>', methods=['GET'])
def get_application(application_id):
    """Get a specific application by ID."""
    try:
        application = get_application_by_id(application_id)
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        return jsonify({
            'success': True,
            'application': application
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting application: {str(e)}")
        return jsonify({'error': f'Failed to get application: {str(e)}'}), 500


@app.route('/api/applications/<application_id>/status', methods=['PUT'])
def update_status(application_id):
    """Update application status (approve/reject)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        status = data.get('status', '').lower()
        remarks = data.get('remarks', '')
        
        if status not in ['approved', 'rejected', 'pending']:
            return jsonify({'error': 'Invalid status. Must be: approved, rejected, or pending'}), 400
        
        # Get application to send email
        application = get_application_by_id(application_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Update status
        success = update_application_status(application_id, status)
        if not success:
            return jsonify({'error': 'Failed to update application status'}), 500
        
        # Send status update email
        try:
            applicant_email = application.get('email')
            applicant_name = application.get('full_name') or application.get('owner_name', 'Applicant')
            loan_type = application.get('loan_type', 'loan')
            
            if applicant_email:
                email_service.send_status_update(
                    to_email=applicant_email,
                    applicant_name=applicant_name,
                    application_id=application_id,
                    loan_type=loan_type,
                    status=status,
                    remarks=remarks
                )
        except Exception as email_error:
            logger.warning(f"Failed to send status update email: {email_error}")
        
        return jsonify({
            'success': True,
            'message': f'Application status updated to {status}',
            'application_id': application_id,
            'status': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating application status: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500


@app.route('/api/applications/<application_id>', methods=['DELETE'])
def delete_application_endpoint(application_id):
    """Delete an application by ID."""
    try:
        # Check if application exists
        application = get_application_by_id(application_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Delete application
        success = delete_application(application_id)
        if not success:
            return jsonify({'error': 'Failed to delete application'}), 500
        
        logger.info(f"Application deleted: {application_id}")
        return jsonify({
            'success': True,
            'message': 'Application deleted successfully',
            'application_id': application_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting application: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to delete application: {str(e)}'}), 500


@app.route('/api/loan-details/<loan_type>', methods=['GET'])
def get_loan_type_details(loan_type):
    """Get loan details for a specific loan type."""
    try:
        details = get_loan_details(loan_type)
        if not details:
            return jsonify({'error': 'Invalid loan type'}), 404
        
        return jsonify({
            'success': True,
            'loan_type': loan_type,
            'details': details
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting loan details: {str(e)}")
        return jsonify({'error': f'Failed to get loan details: {str(e)}'}), 500


@app.route('/api/calculate-emi', methods=['POST'])
def calculate_emi_endpoint():
    """Calculate EMI for given parameters."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        loan_type = data.get('loan_type')
        loan_amount = data.get('loan_amount')
        tenure = data.get('tenure')
        tenure_unit = data.get('tenure_unit', 'years')
        
        if not all([loan_type, loan_amount, tenure]):
            return jsonify({'error': 'Missing required fields: loan_type, loan_amount, tenure'}), 400
        
        emi_info = calculate_emi_for_loan_type(loan_type, loan_amount, tenure, tenure_unit)
        
        return jsonify({
            'success': True,
            'emi_info': emi_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating EMI: {str(e)}")
        return jsonify({'error': f'Failed to calculate EMI: {str(e)}'}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict loan approval for a loan application.
    
    Expected JSON:
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
    """
    try:
        if model is None or preprocessor is None:
            return jsonify({
                'error': 'Model not loaded. Please ensure model is trained and available.'
            }), 500
        
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Sanitize input
        validator = LoanApplicationValidator()
        sanitized_data = validator.sanitize_input(data)
        
        # Validate input
        is_valid, error_message = validator.validate_application(sanitized_data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Predict
        if model_trainer:
            prediction, probability, feature_importance = model_trainer.predict(sanitized_data)
        else:
            # Direct prediction using loaded model
            X_processed = preprocessor.preprocess_single(sanitized_data)
            prediction_proba = model.predict_proba(X_processed)[0]
            prediction_int = model.predict(X_processed)[0]
            prediction = 'Approved' if prediction_int == 1 else 'Rejected'
            probability = float(prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0])
            
            # Get feature importance if available
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                feature_names = model_info.get('feature_names', [])
                feature_importance = dict(zip(feature_names, importances))
                feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        # Prepare response
        response = {
            'prediction': prediction,
            'probability': round(probability * 100, 2),
            'status': 'approved' if prediction == 'Approved' else 'rejected',
            'feature_importance': {k: float(v) for k, v in list(feature_importance.items())[:5]}  # Top 5 features
        }
        
        logger.info(f"Prediction made: {prediction} (probability: {probability:.2%})")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/api/model/performance', methods=['GET'])
def get_model_performance():
    """Get model performance metrics."""
    try:
        if model_info is None:
            return jsonify({'error': 'Model info not available'}), 404
        
        # Get metrics for all models
        all_metrics = {}
        for model_name, metrics in model_info.get('metrics', {}).items():
            all_metrics[model_name] = {
                'accuracy': round(metrics['accuracy'], 4),
                'precision': round(metrics['precision'], 4),
                'recall': round(metrics['recall'], 4),
                'f1_score': round(metrics['f1_score'], 4),
                'roc_auc': round(metrics.get('roc_auc', 0), 4),
                'confusion_matrix': metrics['confusion_matrix']
            }
        
        response = {
            'best_model': model_info.get('best_model_name'),
            'models': all_metrics
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        return jsonify({'error': f'Failed to get performance metrics: {str(e)}'}), 500


@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """Get model information and feature importance."""
    try:
        if model is None or model_info is None:
            return jsonify({'error': 'Model not loaded'}), 404
        
        # Get feature importance
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = model_info.get('feature_names', [])
            feature_importance = {
                name: float(importance) 
                for name, importance in zip(feature_names, importances)
            }
            # Sort by importance
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        response = {
            'model_name': model_info.get('best_model_name'),
            'feature_importance': feature_importance,
            'feature_count': len(model_info.get('feature_names', []))
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({'error': f'Failed to get model info: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        model_status = 'loaded' if model is not None else 'not_loaded'
        return jsonify({
            'status': 'healthy',
            'model_status': model_status,
            'service': 'Loan Approval Prediction System'
        }), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    import traceback
    error_details = traceback.format_exc()
    logger.error(f"Internal server error: {error}")
    logger.error(error_details)
    
    # In debug mode, return more details
    if app.debug:
        return jsonify({
            'error': 'Internal server error',
            'details': str(error),
            'traceback': error_details
        }), 500
    else:
        return jsonify({'error': 'Internal server error. Please check server logs for details.'}), 500


if __name__ == '__main__':
    # Load model on startup (optional for ML prediction feature)
    logger.info("Starting Multi-Loan Application System...")
    try:
        load_model()  # Try to load model, but don't fail if it doesn't exist
    except Exception as e:
        logger.warning(f"ML model not loaded: {e}. System will continue without prediction feature.")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'  # Default to True for better error messages
    app.config['DEBUG'] = debug
    logger.info(f"Starting server on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)

