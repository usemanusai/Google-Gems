# Assets Directory

This directory contains static assets for the Custom Gemini Agent GUI application.

## Contents

- `icon.ico` - Application icon (Windows)
- `icon.png` - Application icon (PNG format)
- `styles/` - Custom stylesheets
- `images/` - Application images and graphics

## Icon Requirements

For the application icon:
- **Windows**: `icon.ico` (16x16, 32x32, 48x48, 256x256 pixels)
- **Cross-platform**: `icon.png` (256x256 pixels recommended)

## Adding Assets

When adding new assets:
1. Place files in appropriate subdirectories
2. Update the PyInstaller spec file (`gemini_gui.spec`) to include new assets
3. Reference assets in code using relative paths from the assets directory
