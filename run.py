#!/usr/bin/env python3
"""
Launcher script for Custom Gemini Agent GUI

This script provides a convenient way to launch the application
with proper error handling and environment setup.
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'PyQt6',
        'sentence_transformers',
        'chromadb',
        'langchain',
        'keyring',
        'loguru',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Error: Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("Custom Gemini Agent GUI")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return 1
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("Dependencies OK")
    
    # Import and run the application
    try:
        from main import main as app_main
        print("Starting application...")
        return app_main()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
