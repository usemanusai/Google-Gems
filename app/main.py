#!/usr/bin/env python3
"""
Custom Gemini Agent GUI - Main Application Entry Point

This is the main entry point for the Custom Gemini Agent GUI application.
It initializes the PyQt6 application and launches the main window.
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from loguru import logger

# Add the app directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from main_window import MainWindow
from services.config_service import ConfigService


def setup_logging():
    """Configure application logging."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler
    log_dir = Path.home() / ".gemini_agent_gui" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "app.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days"
    )


def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting Custom Gemini Agent GUI")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Custom Gemini Agent GUI")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Custom Gemini Agent")
        
        # Set application properties for better Windows integration
        if sys.platform == "win32":
            import ctypes
            # Set the app user model ID for proper taskbar grouping
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CustomGeminiAgent.GUI.1.0")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Initialize configuration service
        config_service = ConfigService()

        # Create and show main window
        main_window = MainWindow(config_service)

        # Show the window
        main_window.show()

        # Center the window on screen
        screen = app.primaryScreen().geometry()
        window_geometry = main_window.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        main_window.move(x, y)
        
        logger.info("Application started successfully")
        
        # Start the event loop
        return app.exec()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
