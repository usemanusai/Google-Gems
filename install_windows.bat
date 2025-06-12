@echo off
echo ========================================
echo Custom Gemini Agent GUI - Windows Setup
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv_gemini
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.8+ is installed
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv_gemini\Scripts\activate.bat

echo Step 3: Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

echo Step 4: Installing Windows-compatible requirements...
echo (This avoids lxml compilation issues)
pip install -r requirements-windows-core-2025.txt
if errorlevel 1 (
    echo ERROR: Installation failed
    echo Trying alternative installation method...
    goto :manual_install
)

echo Step 5: Testing installation...
python test_windows_install.py
if errorlevel 1 (
    echo WARNING: Some packages may not be working correctly
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the application:
echo 1. Activate the virtual environment: venv_gemini\Scripts\activate.bat
echo 2. Run the application: python app\main_window.py
echo.
pause
exit /b 0

:manual_install
echo.
echo Attempting manual installation of core packages...
pip install PyQt6==6.9.1
pip install google-generativeai==0.8.3
pip install chromadb==1.0.12
pip install sentence-transformers==4.1.0
pip install requests==2.32.3
pip install beautifulsoup4==4.12.3
pip install html5lib==1.1
pip install defusedxml==0.7.1
pip install pydantic==2.11.5
pip install loguru==0.7.2
pip install pywin32==310

echo.
echo Manual installation completed.
echo Testing installation...
python test_windows_install.py

echo.
echo ========================================
echo Setup completed with manual installation
echo ========================================
pause
