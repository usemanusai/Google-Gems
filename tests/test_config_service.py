"""
Tests for ConfigService
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add app directory to path for imports
import sys
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from services.config_service import ConfigService, GemConfiguration, AppSettings


class TestConfigService:
    """Test cases for ConfigService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_service(self, temp_dir):
        """Create a ConfigService instance with temporary directory."""
        with patch('pathlib.Path.home', return_value=temp_dir):
            service = ConfigService()
            return service
    
    def test_initialization(self, config_service):
        """Test ConfigService initialization."""
        assert config_service.app_dir.exists()
        assert config_service.config_dir.exists()
        assert config_service.gems_dir.exists()
        assert isinstance(config_service.settings, AppSettings)
    
    def test_settings_save_load(self, config_service):
        """Test settings save and load functionality."""
        # Modify settings
        config_service.settings.auto_save_interval = 600
        config_service.settings.max_chat_history = 2000
        
        # Save settings
        assert config_service.save_settings() is True
        
        # Create new service instance to test loading
        with patch('pathlib.Path.home', return_value=config_service.app_dir.parent):
            new_service = ConfigService()
            assert new_service.settings.auto_save_interval == 600
            assert new_service.settings.max_chat_history == 2000
    
    @patch('keyring.set_password')
    @patch('keyring.get_password')
    def test_api_key_management(self, mock_get, mock_set, config_service):
        """Test API key storage and retrieval."""
        test_key = "test-api-key-12345"
        
        # Test setting API key
        mock_set.return_value = None
        assert config_service.set_api_key(test_key) is True
        mock_set.assert_called_once_with(
            ConfigService.SERVICE_NAME, 
            ConfigService.API_KEY_NAME, 
            test_key
        )
        
        # Test getting API key
        mock_get.return_value = test_key
        retrieved_key = config_service.get_api_key()
        assert retrieved_key == test_key
        mock_get.assert_called_once_with(
            ConfigService.SERVICE_NAME, 
            ConfigService.API_KEY_NAME
        )
    
    def test_gem_configuration_management(self, config_service):
        """Test gem configuration save, load, and list functionality."""
        # Create test gem configuration
        gem_config = GemConfiguration(
            name="test_gem",
            instructions="Test instructions",
            knowledge_sources=["file1.txt", "file2.txt"]
        )
        
        # Save gem configuration
        assert config_service.save_gem_configuration(gem_config) is True
        
        # Load gem configuration
        loaded_config = config_service.load_gem_configuration("test_gem")
        assert loaded_config is not None
        assert loaded_config.name == "test_gem"
        assert loaded_config.instructions == "Test instructions"
        assert loaded_config.knowledge_sources == ["file1.txt", "file2.txt"]
        
        # List gem configurations
        gem_list = config_service.list_gem_configurations()
        assert "test_gem" in gem_list
        
        # Delete gem configuration
        assert config_service.delete_gem_configuration("test_gem") is True
        
        # Verify deletion
        deleted_config = config_service.load_gem_configuration("test_gem")
        assert deleted_config is None
        
        gem_list_after_delete = config_service.list_gem_configurations()
        assert "test_gem" not in gem_list_after_delete
    
    def test_nonexistent_gem_configuration(self, config_service):
        """Test loading nonexistent gem configuration."""
        config = config_service.load_gem_configuration("nonexistent")
        assert config is None
    
    def test_directory_properties(self, config_service):
        """Test directory property methods."""
        assert config_service.get_app_directory() == config_service.app_dir
        assert config_service.get_config_directory() == config_service.config_dir
        assert config_service.get_gems_directory() == config_service.gems_dir


if __name__ == "__main__":
    pytest.main([__file__])
