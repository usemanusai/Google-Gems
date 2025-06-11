#!/usr/bin/env python3
"""
Installation Verification Script for Custom Gemini Agent GUI
This script checks if all required dependencies are properly installed.
"""

import sys
import importlib
import subprocess
from typing import List, Tuple

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed and importable."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✅ {package_name} ({version}) - Installed")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_core_dependencies() -> List[Tuple[str, str, bool]]:
    """Check core dependencies required for basic functionality."""
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("Google Generative AI", "google.generativeai"),
        ("ChromaDB", "chromadb"),
        ("Sentence Transformers", "sentence_transformers"),
        ("Requests", "requests"),
        ("Beautiful Soup", "bs4"),
        ("Pydantic", "pydantic"),
        ("Loguru", "loguru"),
    ]
    
    results = []
    print("\n🔍 Checking Core Dependencies:")
    print("-" * 40)
    
    for name, import_name in dependencies:
        success = check_package(name, import_name)
        results.append((name, import_name, success))
    
    return results

def check_optional_dependencies() -> List[Tuple[str, str, bool]]:
    """Check optional dependencies for enhanced functionality."""
    dependencies = [
        ("PyPDF2", "PyPDF2"),
        ("Python-DOCX", "docx"),
        ("Watchdog", "watchdog"),
        ("GitPython", "git"),
        ("Keyring", "keyring"),
        ("Trafilatura", "trafilatura"),
        ("OpenPyXL", "openpyxl"),
    ]
    
    results = []
    print("\n🔍 Checking Optional Dependencies:")
    print("-" * 40)
    
    for name, import_name in dependencies:
        success = check_package(name, import_name)
        results.append((name, import_name, success))
    
    return results

def check_development_dependencies() -> List[Tuple[str, str, bool]]:
    """Check development dependencies."""
    dependencies = [
        ("Pytest", "pytest"),
        ("Black", "black"),
        ("MyPy", "mypy"),
        ("Flake8", "flake8"),
    ]
    
    results = []
    print("\n🔍 Checking Development Dependencies:")
    print("-" * 40)
    
    for name, import_name in dependencies:
        success = check_package(name, import_name)
        results.append((name, import_name, success))
    
    return results

def test_gui_availability() -> bool:
    """Test if GUI components can be initialized."""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QCoreApplication
        
        # Test if we can create a QApplication
        if not QCoreApplication.instance():
            app = QApplication([])
            print("✅ PyQt6 GUI - Available")
            app.quit()
            return True
        else:
            print("✅ PyQt6 GUI - Available (existing instance)")
            return True
    except Exception as e:
        print(f"❌ PyQt6 GUI - Error: {e}")
        return False

def test_api_imports() -> bool:
    """Test if API-related imports work."""
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI - Import successful")
        return True
    except Exception as e:
        print(f"❌ Google Generative AI - Import failed: {e}")
        return False

def test_vector_db() -> bool:
    """Test if ChromaDB can be initialized."""
    try:
        import chromadb
        # Try to create a client
        client = chromadb.Client()
        print("✅ ChromaDB - Client creation successful")
        return True
    except Exception as e:
        print(f"❌ ChromaDB - Client creation failed: {e}")
        return False

def provide_installation_suggestions(failed_packages: List[str]) -> None:
    """Provide installation suggestions for failed packages."""
    if not failed_packages:
        return
    
    print("\n💡 Installation Suggestions:")
    print("-" * 40)
    
    suggestions = {
        "PyQt6": "pip install PyQt6",
        "Google Generative AI": "pip install google-generativeai",
        "ChromaDB": "pip install chromadb",
        "Sentence Transformers": "pip install sentence-transformers",
        "PyPDF2": "pip install PyPDF2",
        "Python-DOCX": "pip install python-docx",
        "Watchdog": "pip install watchdog",
        "GitPython": "pip install GitPython",
        "Keyring": "pip install keyring",
    }
    
    for package in failed_packages:
        if package in suggestions:
            print(f"📦 {package}: {suggestions[package]}")
    
    print("\n🔧 Alternative installation methods:")
    print("   Standard: pip install -r requirements.txt")
    print("   Flexible: pip install -r requirements-flexible.txt")
    print("   Minimal:  pip install -r requirements-minimal.txt")

def main():
    """Main verification function."""
    print("🔍 Custom Gemini Agent GUI - Installation Verification")
    print("=" * 60)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check dependencies
    core_results = check_core_dependencies()
    optional_results = check_optional_dependencies()
    dev_results = check_development_dependencies()
    
    # Test functionality
    print("\n🧪 Testing Functionality:")
    print("-" * 40)
    gui_ok = test_gui_availability()
    api_ok = test_api_imports()
    db_ok = test_vector_db()
    
    # Summarize results
    print("\n📊 Summary:")
    print("-" * 40)
    
    core_failed = [name for name, _, success in core_results if not success]
    optional_failed = [name for name, _, success in optional_results if not success]
    
    total_core = len(core_results)
    core_success = total_core - len(core_failed)
    
    print(f"Core Dependencies: {core_success}/{total_core} installed")
    print(f"Optional Dependencies: {len(optional_results) - len(optional_failed)}/{len(optional_results)} installed")
    print(f"Functionality Tests: {sum([gui_ok, api_ok, db_ok])}/3 passed")
    
    if core_failed:
        print(f"\n❌ Missing core dependencies: {', '.join(core_failed)}")
        provide_installation_suggestions(core_failed)
        print("\n⚠️  Application may not work properly without core dependencies.")
    else:
        print("\n✅ All core dependencies are installed!")
        if optional_failed:
            print(f"ℹ️  Optional features may be limited due to missing: {', '.join(optional_failed)}")
        else:
            print("✅ All optional dependencies are also installed!")
    
    if python_ok and not core_failed and gui_ok and api_ok and db_ok:
        print("\n🎉 Installation verification PASSED! You're ready to use the Custom Gemini Agent GUI.")
        return 0
    else:
        print("\n⚠️  Installation verification FAILED. Please install missing dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
