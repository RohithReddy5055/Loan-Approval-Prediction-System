"""
Setup script for Loan Approval Prediction System.
This script helps set up the project environment.
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Loan Approval Prediction System - Setup")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro} ✓")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies..."):
        print("Failed to install dependencies. Please install manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create necessary directories
    directories = [
        'models/trained_models',
        'data',
        'static/css',
        'static/js',
        'static/images',
        'templates',
        'utils',
        'tests'
    ]
    
    print("\nCreating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # Generate dataset
    print("\nGenerating sample dataset...")
    if Path('generate_dataset.py').exists():
        if run_command("python generate_dataset.py", "Generating loan dataset..."):
            print("Dataset generated successfully!")
        else:
            print("Warning: Failed to generate dataset. You can generate it manually later.")
    else:
        print("Warning: generate_dataset.py not found")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Train the models: python train_model.py")
    print("2. Start the application: python app.py")
    print("3. Open your browser: http://localhost:5000")
    print("\nFor more information, see README.md")

if __name__ == '__main__':
    main()

