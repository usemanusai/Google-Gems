"""
Tests for MainWindow
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from main_window import MainWindow
from services.config_service import ConfigService


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def mock_config_service():
    """Create a mock config service."""
    mock_service = MagicMock(spec=ConfigService)
    mock_service.get_api_key.return_value = None
    mock_service.settings = MagicMock()
    mock_service.settings.auto_save_interval = 300
    return mock_service


class TestMainWindow:
    """Test cases for MainWindow."""
    
    def test_main_window_initialization(self, qapp, mock_config_service):
        """Test MainWindow initialization."""
        with patch('main_window.MainController') as mock_controller:
            # Setup mock controller
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance
            mock_controller_instance.initialize.return_value = True
            
            # Create main window
            window = MainWindow(mock_config_service)
            
            # Verify window was created
            assert window is not None
            assert window.windowTitle() == "Custom Gemini Agent GUI"
            
            # Verify controller was initialized
            mock_controller.assert_called_once()
            mock_controller_instance.initialize.assert_called_once()
    
    def test_ui_components_exist(self, qapp, mock_config_service):
        """Test that all UI components are created."""
        with patch('main_window.MainController') as mock_controller:
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance
            mock_controller_instance.initialize.return_value = True
            
            window = MainWindow(mock_config_service)
            
            # Check that widgets exist
            assert hasattr(window, 'instructions_widget')
            assert hasattr(window, 'knowledge_widget')
            assert hasattr(window, 'chat_widget')
            assert hasattr(window, 'controller')
            assert hasattr(window, 'message_worker')
    
    def test_menu_actions(self, qapp, mock_config_service):
        """Test menu actions."""
        with patch('main_window.MainController') as mock_controller:
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance
            mock_controller_instance.initialize.return_value = True
            
            window = MainWindow(mock_config_service)
            
            # Test that menu bar exists
            menu_bar = window.menuBar()
            assert menu_bar is not None
            
            # Check for main menus
            menus = [action.text() for action in menu_bar.actions()]
            assert '&File' in menus
            assert '&Settings' in menus
            assert '&Help' in menus
    
    def test_status_bar(self, qapp, mock_config_service):
        """Test status bar functionality."""
        with patch('main_window.MainController') as mock_controller:
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance
            mock_controller_instance.initialize.return_value = True
            
            window = MainWindow(mock_config_service)
            
            # Check status bar exists
            status_bar = window.statusBar()
            assert status_bar is not None
            
            # Test status message
            test_message = "Test status message"
            status_bar.showMessage(test_message)
            assert status_bar.currentMessage() == test_message
    
    @patch('main_window.QInputDialog.getText')
    def test_new_gem_configuration(self, mock_input_dialog, qapp, mock_config_service):
        """Test creating a new gem configuration."""
        with patch('main_window.MainController') as mock_controller:
            mock_controller_instance = MagicMock()
            mock_controller.return_value = mock_controller_instance
            mock_controller_instance.initialize.return_value = True
            mock_controller_instance.create_new_gem_configuration.return_value = True
            
            # Setup input dialog mock
            mock_input_dialog.return_value = ("Test Agent", True)
            
            window = MainWindow(mock_config_service)
            
            # Call new configuration method
            window.new_gem_configuration()
            
            # Verify controller method was called
            mock_controller_instance.create_new_gem_configuration.assert_called_once_with("Test Agent")
    
    def test_message_worker_integration(self, qapp, mock_config_service):
        """Test message worker integration."""
        with patch('main_window.MainController') as mock_controller:
            with patch('main_window.MessageWorker') as mock_worker:
                mock_controller_instance = MagicMock()
                mock_controller.return_value = mock_controller_instance
                mock_controller_instance.initialize.return_value = True
                
                mock_worker_instance = MagicMock()
                mock_worker.return_value = mock_worker_instance
                
                window = MainWindow(mock_config_service)
                
                # Verify worker was created
                mock_worker.assert_called_once_with(mock_controller_instance)
                
                # Test message sending
                test_message = "Hello, AI!"
                window.on_message_sent(test_message)
                
                # Verify worker send_message was called
                mock_worker_instance.send_message.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
