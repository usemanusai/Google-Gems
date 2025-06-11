#!/usr/bin/env python3
"""
Build Script for Custom Gemini Agent GUI

This script builds the application into a standalone executable using PyInstaller.
"""

import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {command}")
        print(f"  Error: {e.stderr}")
        return False


def clean_build_directories():
    """Clean previous build artifacts."""
    print("Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            file_path.unlink()
            print(f"  Removed {file_path}")
    
    print("✓ Build directories cleaned")


def create_pyinstaller_spec():
    """Create PyInstaller spec file."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'sentence_transformers',
        'chromadb',
        'langchain',
        'google.generativeai',
        'keyring',
        'loguru',
        'pydantic',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = []
for d in a.datas:
    if 'pyconfig' not in d[0]:
        pyd.append(d)
a.datas = pyd

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CustomGeminiAgentGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
)
'''
    
    try:
        with open('gemini_gui.spec', 'w') as f:
            f.write(spec_content)
        print("✓ Created PyInstaller spec file")
        return True
    except Exception as e:
        print(f"✗ Failed to create spec file: {e}")
        return False


def build_executable():
    """Build the executable using PyInstaller."""
    commands = [
        ("pyinstaller gemini_gui.spec", "Building executable with PyInstaller"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def create_installer():
    """Create an installer (Windows only)."""
    if sys.platform != "win32":
        print("Installer creation is only supported on Windows")
        return True
    
    # Check if NSIS is available
    try:
        subprocess.run("makensis", shell=True, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("NSIS not found - skipping installer creation")
        print("Install NSIS from https://nsis.sourceforge.io/ to create installers")
        return True
    
    # Create NSIS script
    nsis_script = '''
!define APPNAME "Custom Gemini Agent GUI"
!define COMPANYNAME "Custom Gemini Agent"
!define DESCRIPTION "Desktop interface for Google Gemini API with RAG capabilities"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"

Name "${APPNAME}"
Icon "assets\\icon.ico"
outFile "CustomGeminiAgentGUI-Setup.exe"

page directory
page instfiles

section "install"
    setOutPath $INSTDIR
    file /r "dist\\CustomGeminiAgentGUI.exe"
    
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\CustomGeminiAgentGUI.exe"
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\CustomGeminiAgentGUI.exe"
sectionEnd

section "uninstall"
    delete "$INSTDIR\\CustomGeminiAgentGUI.exe"
    delete "$INSTDIR\\uninstall.exe"
    rmDir "$INSTDIR"
    
    delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${COMPANYNAME}"
    delete "$DESKTOP\\${APPNAME}.lnk"
sectionEnd
'''
    
    try:
        with open('installer.nsi', 'w') as f:
            f.write(nsis_script)
        
        return run_command("makensis installer.nsi", "Creating Windows installer")
    except Exception as e:
        print(f"✗ Failed to create installer: {e}")
        return False


def verify_build():
    """Verify the build was successful."""
    exe_path = Path("dist/CustomGeminiAgentGUI.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ Executable created: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print("✗ Executable not found in dist/")
        return False


def main():
    """Main build function."""
    print("Custom Gemini Agent GUI - Build Script")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_directories()
    
    # Create spec file
    if not create_pyinstaller_spec():
        return 1
    
    # Build executable
    if not build_executable():
        print("\n✗ Build failed")
        return 1
    
    # Verify build
    if not verify_build():
        return 1
    
    # Create installer (optional)
    create_installer()
    
    print("\n✓ Build completed successfully!")
    print(f"Executable: {Path('dist/CustomGeminiAgentGUI.exe').absolute()}")
    
    if Path("CustomGeminiAgentGUI-Setup.exe").exists():
        print(f"Installer: {Path('CustomGeminiAgentGUI-Setup.exe').absolute()}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
