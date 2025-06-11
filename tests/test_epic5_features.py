"""
Tests for Epic 5: Configuration & Session Management
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add app directory to path for imports
import sys
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from services.template_service import TemplateService
from services.workspace_service import WorkspaceService
from services.import_export_service import ImportExportService
from services.session_service import SessionService
from services.config_service import ConfigService
from models.workspace import (
    ConfigurationTemplate, EnhancedGemConfiguration, Workspace, 
    WorkspaceType, ConfigurationExport, SessionState
)


class TestConfigurationTemplate:
    """Test cases for ConfigurationTemplate model."""
    
    def test_template_creation(self):
        """Test creating a configuration template."""
        template = ConfigurationTemplate(
            name="Test Template",
            description="A test template",
            category="testing",
            instructions="You are a test assistant.",
            tags=["test", "demo"]
        )
        
        assert template.name == "Test Template"
        assert template.category == "testing"
        assert template.is_builtin is False
        assert len(template.tags) == 2
        assert template.id is not None
        assert template.version == "1.0.0"


class TestEnhancedGemConfiguration:
    """Test cases for EnhancedGemConfiguration model."""
    
    def test_enhanced_config_creation(self):
        """Test creating an enhanced configuration."""
        config = EnhancedGemConfiguration(
            name="Test Config",
            instructions="Test instructions",
            description="A test configuration",
            category="testing"
        )
        
        assert config.name == "Test Config"
        assert config.usage_count == 0
        assert config.total_messages == 0
        assert config.is_shared is False
        assert config.id is not None
    
    def test_usage_tracking(self):
        """Test usage tracking functionality."""
        config = EnhancedGemConfiguration(name="Test Config")
        
        initial_usage = config.usage_count
        initial_modified = config.modified_at
        
        config.update_usage()
        
        assert config.usage_count == initial_usage + 1
        assert config.last_used_at is not None
        assert config.modified_at > initial_modified
    
    def test_message_tracking(self):
        """Test message tracking functionality."""
        config = EnhancedGemConfiguration(name="Test Config")
        
        initial_messages = config.total_messages
        
        config.add_message()
        
        assert config.total_messages == initial_messages + 1


class TestWorkspace:
    """Test cases for Workspace model."""
    
    def test_workspace_creation(self):
        """Test creating a workspace."""
        workspace = Workspace(
            name="Test Workspace",
            description="A test workspace",
            workspace_type=WorkspaceType.PROJECT
        )
        
        assert workspace.name == "Test Workspace"
        assert workspace.workspace_type == WorkspaceType.PROJECT
        assert len(workspace.configurations) == 0
        assert workspace.is_shared is False
    
    def test_configuration_management(self):
        """Test adding and removing configurations."""
        workspace = Workspace(name="Test Workspace")
        
        config_id = "test_config_123"
        
        # Add configuration
        workspace.add_configuration(config_id)
        assert config_id in workspace.configurations
        
        # Remove configuration
        workspace.remove_configuration(config_id)
        assert config_id not in workspace.configurations


class TestTemplateService:
    """Test cases for TemplateService."""
    
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
    
    @pytest.fixture
    def template_service(self, config_service):
        """Create a TemplateService instance."""
        return TemplateService(config_service)
    
    def test_template_service_initialization(self, template_service):
        """Test template service initialization."""
        assert template_service is not None
        assert template_service.templates_dir.exists()
    
    def test_save_and_load_template(self, template_service):
        """Test saving and loading templates."""
        template = ConfigurationTemplate(
            name="Test Template",
            description="A test template",
            instructions="Test instructions"
        )
        
        # Save template
        assert template_service.save_template(template) is True
        
        # Load template
        loaded_template = template_service.load_template("Test Template")
        assert loaded_template is not None
        assert loaded_template.name == "Test Template"
        assert loaded_template.instructions == "Test instructions"
    
    def test_list_templates(self, template_service):
        """Test listing templates."""
        # Create test templates
        template1 = ConfigurationTemplate(name="Template 1", category="test")
        template2 = ConfigurationTemplate(name="Template 2", category="demo")
        
        template_service.save_template(template1)
        template_service.save_template(template2)
        
        # List all templates
        all_templates = template_service.list_templates()
        assert len(all_templates) >= 2
        
        # List by category
        test_templates = template_service.list_templates(category="test")
        assert len(test_templates) >= 1
        assert any(t.name == "Template 1" for t in test_templates)
    
    def test_builtin_templates(self, template_service):
        """Test that built-in templates are created."""
        templates = template_service.list_templates()
        
        # Should have built-in templates
        builtin_templates = [t for t in templates if t.is_builtin]
        assert len(builtin_templates) > 0
        
        # Check for specific built-in templates
        template_names = [t.name for t in builtin_templates]
        assert "Research Assistant" in template_names
        assert "Code Assistant" in template_names


class TestWorkspaceService:
    """Test cases for WorkspaceService."""
    
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
    
    @pytest.fixture
    def workspace_service(self, config_service):
        """Create a WorkspaceService instance."""
        return WorkspaceService(config_service)
    
    def test_workspace_service_initialization(self, workspace_service):
        """Test workspace service initialization."""
        assert workspace_service is not None
        assert workspace_service.workspaces_dir.exists()
        assert workspace_service.configurations_dir.exists()
    
    def test_default_workspace_creation(self, workspace_service):
        """Test that default workspace is created."""
        default_workspace = workspace_service.load_workspace("default")
        assert default_workspace is not None
        assert default_workspace.name == "Default Workspace"
    
    def test_create_and_load_workspace(self, workspace_service):
        """Test creating and loading workspaces."""
        workspace = workspace_service.create_workspace(
            name="Test Workspace",
            description="A test workspace",
            workspace_type=WorkspaceType.PROJECT
        )
        
        assert workspace is not None
        assert workspace.name == "Test Workspace"
        
        # Load workspace
        loaded_workspace = workspace_service.load_workspace(workspace.id)
        assert loaded_workspace is not None
        assert loaded_workspace.name == "Test Workspace"
    
    def test_configuration_management(self, workspace_service):
        """Test configuration management in workspaces."""
        # Create workspace
        workspace = workspace_service.create_workspace("Test Workspace")
        
        # Create configuration
        config = EnhancedGemConfiguration(
            name="Test Config",
            instructions="Test instructions"
        )
        
        # Save configuration
        assert workspace_service.save_configuration(config) is True
        
        # Add to workspace
        assert workspace_service.add_configuration_to_workspace(workspace.id, config.id) is True
        
        # Check workspace contains configuration
        updated_workspace = workspace_service.load_workspace(workspace.id)
        assert config.id in updated_workspace.configurations
        
        # List configurations for workspace
        configs = workspace_service.list_configurations(workspace.id)
        assert len(configs) == 1
        assert configs[0].name == "Test Config"


class TestImportExportService:
    """Test cases for ImportExportService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def services(self, temp_dir):
        """Create service instances."""
        with patch('pathlib.Path.home', return_value=temp_dir):
            config_service = ConfigService()
            workspace_service = WorkspaceService(config_service)
            template_service = TemplateService(config_service)
            import_export_service = ImportExportService(
                config_service, workspace_service, template_service
            )
            
            return {
                "config": config_service,
                "workspace": workspace_service,
                "template": template_service,
                "import_export": import_export_service
            }
    
    def test_export_configuration(self, services):
        """Test exporting a configuration."""
        workspace_service = services["workspace"]
        import_export_service = services["import_export"]
        
        # Create and save configuration
        config = EnhancedGemConfiguration(
            name="Test Config",
            instructions="Test instructions"
        )
        workspace_service.save_configuration(config)
        
        # Export configuration
        export_path = import_export_service.export_configuration(config.id)
        
        assert export_path is not None
        assert Path(export_path).exists()
        
        # Verify export content
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert "configurations" in export_data
        assert len(export_data["configurations"]) == 1
        assert export_data["configurations"][0]["name"] == "Test Config"
    
    def test_import_configuration(self, services):
        """Test importing configurations."""
        import_export_service = services["import_export"]
        
        # Create test export data
        config_data = EnhancedGemConfiguration(
            name="Imported Config",
            instructions="Imported instructions"
        )
        
        export_data = ConfigurationExport(
            configurations=[config_data]
        )
        
        # Create temporary export file
        temp_file = Path(tempfile.mktemp(suffix=".json"))
        with open(temp_file, 'w') as f:
            json.dump(export_data.model_dump(), f, default=str)
        
        try:
            # Import from file
            results = import_export_service.import_from_file(str(temp_file))
            
            assert "error" not in results
            assert results["configurations"]["imported"] == 1
            assert results["configurations"]["errors"] == 0
            
        finally:
            temp_file.unlink()


class TestSessionService:
    """Test cases for SessionService."""
    
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
    
    @pytest.fixture
    def session_service(self, config_service):
        """Create a SessionService instance."""
        return SessionService(config_service)
    
    def test_session_service_initialization(self, session_service):
        """Test session service initialization."""
        assert session_service is not None
        assert session_service.current_session is not None
        assert session_service.sessions_dir.exists()
    
    def test_workspace_and_configuration_tracking(self, session_service):
        """Test workspace and configuration tracking."""
        # Set current workspace
        session_service.set_current_workspace("test_workspace")
        assert session_service.get_current_workspace_id() == "test_workspace"
        
        # Set current configuration
        session_service.set_current_configuration("test_config")
        assert session_service.get_current_configuration_id() == "test_config"
        
        # Check recent configurations
        recent = session_service.get_recent_configurations()
        assert "test_config" in recent
    
    def test_window_geometry_persistence(self, session_service):
        """Test window geometry saving and loading."""
        geometry = {"x": 100, "y": 200, "width": 800, "height": 600}
        
        # Save geometry
        session_service.save_window_geometry(geometry)
        
        # Load geometry
        loaded_geometry = session_service.get_window_geometry()
        assert loaded_geometry == geometry
    
    def test_panel_state_persistence(self, session_service):
        """Test panel state saving and loading."""
        # Save panel state
        session_service.save_panel_state("left_panel", False)
        session_service.save_panel_state("right_panel", True)
        
        # Load panel states
        assert session_service.get_panel_state("left_panel") is False
        assert session_service.get_panel_state("right_panel") is True
        assert session_service.get_panel_state("unknown_panel", True) is True
    
    def test_session_statistics(self, session_service):
        """Test session statistics."""
        stats = session_service.get_session_statistics()
        
        assert "session_id" in stats
        assert "created_at" in stats
        assert "last_active_at" in stats
        assert "session_duration" in stats


if __name__ == "__main__":
    pytest.main([__file__])
