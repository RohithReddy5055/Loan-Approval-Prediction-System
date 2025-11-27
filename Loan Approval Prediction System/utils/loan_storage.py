"""
Storage utilities for loan applications.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage file path - prefer project root, fallback to temp directory
# OneDrive may prevent file writes, so we use temp directory as reliable fallback
import os
import tempfile

PROJECT_ROOT = Path(os.getcwd())
PROJECT_STORAGE_FILE = PROJECT_ROOT / 'applications.json'
TEMP_STORAGE_FILE = Path(tempfile.gettempdir()) / 'loan_applications.json'

# Try project root first, use temp if project root is not writable
STORAGE_FILE = PROJECT_STORAGE_FILE


def ensure_storage_dir():
    """Ensure storage file location is accessible (no directory creation needed)."""
    # Since we're storing directly in project root, just verify project root exists
    if not PROJECT_ROOT.exists():
        raise Exception(f"Project root directory does not exist: {PROJECT_ROOT}")
    logger.debug(f"Storage file will be at: {STORAGE_FILE}")


def get_storage_file_path():
    """Get the storage file path, checking both locations."""
    # Check if project root file exists
    if PROJECT_STORAGE_FILE.exists():
        return PROJECT_STORAGE_FILE
    # Check if temp file exists
    if TEMP_STORAGE_FILE.exists():
        return TEMP_STORAGE_FILE
    # Default to project root for new files
    return PROJECT_STORAGE_FILE

def load_applications() -> List[Dict]:
    """Load all applications from storage."""
    ensure_storage_dir()
    
    storage_file = get_storage_file_path()
    
    if not storage_file.exists():
        return []
    
    try:
        with open(storage_file, 'r', encoding='utf-8') as f:
            applications = json.load(f)
            return applications if isinstance(applications, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading applications: {e}")
        return []


def save_application(application: Dict) -> bool:
    """Save a new application to storage."""
    try:
        ensure_storage_dir()
        applications = load_applications()
        
        # Clean application data for JSON serialization
        cleaned_application = clean_for_json(application)
        
        # Add application
        applications.append(cleaned_application)
        
        # Try saving to project root first, fallback to temp directory
        storage_file = PROJECT_STORAGE_FILE
        storage_file_path = str(storage_file)
        
        try:
            # Try to write to project root
            with open(storage_file_path, 'w', encoding='utf-8') as f:
                json.dump(applications, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Application saved: {cleaned_application.get('application_id')} to {storage_file_path}")
            return True
        except (IOError, OSError, PermissionError) as e:
            # If project root write fails (e.g., OneDrive restrictions), use temp directory
            logger.warning(f"Cannot write to project directory ({e}), using temp directory instead")
            storage_file = TEMP_STORAGE_FILE
            storage_file_path = str(storage_file)
            
            try:
                with open(storage_file_path, 'w', encoding='utf-8') as f:
                    json.dump(applications, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Application saved to temp location: {cleaned_application.get('application_id')} to {storage_file_path}")
                return True
            except Exception as temp_error:
                logger.error(f"Error saving to temp directory: {temp_error}")
                raise temp_error
        
    except Exception as e:
        logger.error(f"Error saving application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def clean_for_json(obj):
    """Clean object for JSON serialization."""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        # Convert other types to string
        return str(obj)


def get_applications_by_type(loan_type: str) -> List[Dict]:
    """Get all applications of a specific loan type."""
    applications = load_applications()
    return [app for app in applications if app.get('loan_type') == loan_type]


def get_all_applications() -> List[Dict]:
    """Get all applications."""
    return load_applications()


def get_application_by_id(application_id: str) -> Optional[Dict]:
    """Get a specific application by ID."""
    applications = load_applications()
    for app in applications:
        if app.get('application_id') == application_id:
            return app
    return None


def update_application_status(application_id: str, status: str) -> bool:
    """Update application status."""
    try:
        applications = load_applications()
        storage_file = get_storage_file_path()
        
        for app in applications:
            if app.get('application_id') == application_id:
                app['status'] = status
                app['updated_at'] = datetime.now().isoformat()
                
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(applications, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Application status updated: {application_id} -> {status}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error updating application status: {e}")
        return False


def delete_application(application_id: str) -> bool:
    """Delete an application by ID."""
    try:
        applications = load_applications()
        storage_file = get_storage_file_path()
        
        # Find and remove the application
        initial_count = len(applications)
        applications = [app for app in applications if app.get('application_id') != application_id]
        
        # Check if application was found and removed
        if len(applications) == initial_count:
            logger.warning(f"Application not found for deletion: {application_id}")
            return False
        
        # Save updated applications list
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(applications, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Application deleted: {application_id}")
            return True
        except (IOError, OSError, PermissionError) as e:
            # If project root write fails, try temp directory
            logger.warning(f"Cannot write to project directory ({e}), using temp directory instead")
            temp_storage_file = TEMP_STORAGE_FILE
            try:
                with open(str(temp_storage_file), 'w', encoding='utf-8') as f:
                    json.dump(applications, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Application deleted from temp location: {application_id}")
                return True
            except Exception as temp_error:
                logger.error(f"Error saving to temp directory: {temp_error}")
                raise temp_error
        
    except Exception as e:
        logger.error(f"Error deleting application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

