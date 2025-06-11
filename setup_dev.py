#!/usr/bin/env python3
"""
Development Setup Script

This script helps set up the development environment for the Custom Gemini Agent GUI.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {command}")
        print(f"  Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("  Python 3.8 or higher is required")
        return False


def install_dependencies():
    """Install project dependencies."""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing project dependencies"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def setup_pre_commit():
    """Set up pre-commit hooks."""
    commands = [
        ("pip install pre-commit", "Installing pre-commit"),
        ("pre-commit install", "Setting up pre-commit hooks"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"Warning: {description} failed (optional)")
    
    return True


def create_pre_commit_config():
    """Create pre-commit configuration file."""
    config_content = """repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --ignore=E203,W503]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
"""
    
    try:
        with open('.pre-commit-config.yaml', 'w') as f:
            f.write(config_content)
        print("✓ Created .pre-commit-config.yaml")
        return True
    except Exception as e:
        print(f"✗ Failed to create .pre-commit-config.yaml: {e}")
        return False


def run_tests():
    """Run the test suite."""
    return run_command("python -m pytest tests/ -v", "Running tests")


def create_vscode_settings():
    """Create VS Code settings for the project."""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "python.defaultInterpreterPath": "./venv/bin/python",
        "python.linting.enabled": True,
        "python.linting.flake8Enabled": True,
        "python.linting.mypyEnabled": True,
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": ["--line-length=100"],
        "editor.formatOnSave": True,
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            ".pytest_cache": True,
            ".mypy_cache": True,
            "*.egg-info": True
        }
    }
    
    try:
        import json
        with open(vscode_dir / "settings.json", 'w') as f:
            json.dump(settings, f, indent=2)
        print("✓ Created VS Code settings")
        return True
    except Exception as e:
        print(f"✗ Failed to create VS Code settings: {e}")
        return False


def main():
    """Main setup function."""
    print("Custom Gemini Agent GUI - Development Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Failed to install dependencies")
        return 1
    
    # Create pre-commit config
    create_pre_commit_config()
    
    # Setup pre-commit (optional)
    setup_pre_commit()
    
    # Create VS Code settings (optional)
    create_vscode_settings()
    
    # Run tests to verify setup
    print("\nVerifying setup by running tests...")
    if run_tests():
        print("\n✓ Development environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Configure your Google Gemini API key in the application")
        print("2. Run the application: python run.py")
        print("3. Start developing!")
    else:
        print("\n⚠ Setup completed but tests failed")
        print("You may need to install additional dependencies or fix test issues")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
