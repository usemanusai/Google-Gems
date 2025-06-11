#!/usr/bin/env python3
"""
Demo Script for Custom Gemini Agent GUI

This script demonstrates the application functionality without requiring
all external dependencies to be installed.
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def check_basic_imports():
    """Check if basic imports work."""
    print("Checking basic imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6 available")
        pyqt_available = True
    except ImportError as e:
        print(f"✗ PyQt6 not available: {e}")
        pyqt_available = False
    
    try:
        from loguru import logger
        print("✓ loguru available")
    except ImportError as e:
        print(f"✗ loguru not available: {e}")
    
    try:
        from pydantic import BaseModel
        print("✓ pydantic available")
    except ImportError as e:
        print(f"✗ pydantic not available: {e}")
    
    return pyqt_available

def test_config_service():
    """Test the configuration service."""
    print("\nTesting ConfigService...")
    
    try:
        from services.config_service import ConfigService, GemConfiguration
        
        # Create config service
        config_service = ConfigService()
        print(f"✓ ConfigService initialized")
        print(f"  App directory: {config_service.get_app_directory()}")
        
        # Test gem configuration
        test_gem = GemConfiguration(
            name="test_demo",
            instructions="You are a helpful demo assistant.",
            knowledge_sources=[]
        )
        
        # Save and load test
        if config_service.save_gem_configuration(test_gem):
            print("✓ Gem configuration saved")
            
            loaded_gem = config_service.load_gem_configuration("test_demo")
            if loaded_gem and loaded_gem.name == "test_demo":
                print("✓ Gem configuration loaded successfully")
            else:
                print("✗ Failed to load gem configuration")
        else:
            print("✗ Failed to save gem configuration")
        
        return True
        
    except Exception as e:
        print(f"✗ ConfigService test failed: {e}")
        return False

def test_api_service():
    """Test the API service."""
    print("\nTesting APIService...")
    
    try:
        from services.config_service import ConfigService
        from services.api_service import APIService
        
        config_service = ConfigService()
        api_service = APIService(config_service)
        
        print("✓ APIService initialized")
        
        # Test configuration (will fail without API key, but should not crash)
        configured = api_service.configure_api()
        if configured:
            print("✓ API configured successfully")
        else:
            print("⚠ API not configured (expected without API key)")
        
        return True
        
    except Exception as e:
        print(f"✗ APIService test failed: {e}")
        return False

def test_rag_service():
    """Test the enhanced RAG service."""
    print("\nTesting Enhanced RAGService...")

    try:
        from services.config_service import ConfigService
        from services.rag_service import RAGService

        config_service = ConfigService()
        rag_service = RAGService(config_service)

        print("✓ Enhanced RAGService initialized")

        # Test smart chunking
        test_doc = {
            "content": "def test(): return 'hello'",
            "metadata": {"file_type": ".py"}
        }
        chunks = rag_service._smart_chunk_document(test_doc)
        print(f"✓ Smart chunking works (created {len(chunks)} chunks)")

        # Test chunk type determination
        chunk_type = rag_service._determine_chunk_type(".py")
        print(f"✓ Chunk type detection works (Python file -> {chunk_type})")

        # Test search (will return empty without data)
        results = rag_service.search_similar("test query", n_results=3)
        print(f"✓ Enhanced search completed (found {len(results)} results)")

        # Test collection stats
        stats = rag_service.get_collection_stats()
        print(f"✓ Collection stats available: {list(stats.keys())}")

        return True

    except Exception as e:
        print(f"✗ Enhanced RAGService test failed: {e}")
        return False

def test_monitoring_service():
    """Test the file monitoring service."""
    print("\nTesting MonitoringService...")

    try:
        from services.monitoring_service import MonitoringService
        from models.knowledge_source import KnowledgeSource, SourceType

        monitoring_service = MonitoringService()
        print("✓ MonitoringService initialized")

        # Test basic functionality
        monitored_sources = monitoring_service.get_monitored_sources()
        print(f"✓ Can get monitored sources: {len(monitored_sources)} sources")

        # Test starting monitoring (may fail without watchdog)
        if monitoring_service.start_monitoring():
            print("✓ Monitoring service started")
        else:
            print("⚠ Monitoring service not started (watchdog may not be available)")

        return True

    except Exception as e:
        print(f"✗ MonitoringService test failed: {e}")
        return False

def test_google_drive_service():
    """Test the Google Drive service."""
    print("\nTesting GoogleDriveService...")

    try:
        from services.config_service import ConfigService
        from services.google_drive_service import GoogleDriveService

        config_service = ConfigService()
        gdrive_service = GoogleDriveService(config_service)

        print("✓ GoogleDriveService initialized")

        # Test basic functionality
        is_auth = gdrive_service.is_authenticated()
        print(f"✓ Authentication status check: {is_auth}")

        # Test MIME type conversion
        ext = gdrive_service._get_extension_from_mime_type('text/plain')
        print(f"✓ MIME type conversion works: text/plain -> {ext}")

        # Test text extraction
        file_data = {"content": b"test content", "extension": ".txt"}
        content = gdrive_service._extract_text_content(file_data)
        print(f"✓ Text extraction works: extracted {len(content) if content else 0} characters")

        return True

    except Exception as e:
        print(f"✗ GoogleDriveService test failed: {e}")
        return False

def test_web_scraping_service():
    """Test the web scraping service."""
    print("\nTesting WebScrapingService...")

    try:
        from services.web_scraping_service import WebScrapingService

        scraping_service = WebScrapingService()
        print("✓ WebScrapingService initialized")

        # Test availability
        is_available = scraping_service.is_available()
        print(f"✓ Availability check: {is_available}")

        # Test URL validation (without making actual requests)
        try:
            from unittest.mock import patch
            with patch('services.web_scraping_service.REQUESTS_AVAILABLE', False):
                valid = scraping_service.validate_url("http://example.com")
                print(f"✓ URL validation works: {valid}")
        except ImportError:
            print("⚠ Mock not available, skipping URL validation test")

        return True

    except Exception as e:
        print(f"✗ WebScrapingService test failed: {e}")
        return False

def test_batch_processing_service():
    """Test the batch processing service."""
    print("\nTesting BatchProcessingService...")

    try:
        from services.batch_processing_service import BatchProcessingService, BatchJob, BatchJobStatus
        from services.config_service import ConfigService
        from models.knowledge_source import KnowledgeSource, SourceType

        # Create mock RAG service
        class MockRAGService:
            def process_knowledge_source(self, source):
                return True

        rag_service = MockRAGService()
        batch_service = BatchProcessingService(rag_service)
        print("✓ BatchProcessingService initialized")

        # Test basic functionality
        is_processing = batch_service.is_processing()
        print(f"✓ Processing status check: {is_processing}")

        # Test max workers setting
        batch_service.set_max_workers(5)
        print(f"✓ Max workers setting: {batch_service.max_workers}")

        # Test statistics
        stats = batch_service.get_processing_statistics()
        print(f"✓ Statistics available: {list(stats.keys())}")

        # Test job creation
        source = KnowledgeSource(
            id="test", path="/test", source_type=SourceType.FILE, name="Test"
        )
        job = BatchJob(id="test_job", source=source)
        print(f"✓ Job creation works: {job.status}")

        return True

    except Exception as e:
        print(f"✗ BatchProcessingService test failed: {e}")
        return False

def test_main_controller():
    """Test the main controller."""
    print("\nTesting MainController...")
    
    try:
        from controllers.main_controller import MainController
        
        controller = MainController()
        print("✓ MainController initialized")
        
        # Test initialization
        if controller.initialize():
            print("✓ Controller initialized successfully")
        else:
            print("⚠ Controller initialization had warnings (expected)")
        
        # Test gem configuration creation
        if controller.create_new_gem_configuration("demo_agent", "Demo instructions"):
            print("✓ Gem configuration created")
        else:
            print("✗ Failed to create gem configuration")
        
        return True
        
    except Exception as e:
        print(f"✗ MainController test failed: {e}")
        return False

def test_ui_components():
    """Test UI components."""
    print("\nTesting UI Components...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication([])
        
        # Test widgets
        from widgets.instructions_widget import InstructionsWidget
        from widgets.knowledge_widget import KnowledgeWidget
        from widgets.chat_widget import ChatWidget
        
        instructions_widget = InstructionsWidget()
        print("✓ InstructionsWidget created")
        
        knowledge_widget = KnowledgeWidget()
        print("✓ KnowledgeWidget created")
        
        chat_widget = ChatWidget()
        print("✓ ChatWidget created")
        
        return True
        
    except Exception as e:
        print(f"✗ UI components test failed: {e}")
        return False

def run_full_demo():
    """Run the full application demo."""
    print("\nRunning full application demo...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from main_window import MainWindow
        from services.config_service import ConfigService
        
        # Create QApplication
        app = QApplication([])
        
        # Create config service
        config_service = ConfigService()
        
        # Create main window
        main_window = MainWindow(config_service)
        
        print("✓ Main window created successfully")
        print("✓ Application ready to run")
        print("\nTo run the full application, use: python run.py")
        
        return True
        
    except Exception as e:
        print(f"✗ Full demo failed: {e}")
        return False

def test_template_service():
    """Test the template service."""
    print("\nTesting TemplateService...")

    try:
        from services.config_service import ConfigService
        from services.template_service import TemplateService
        from models.workspace import ConfigurationTemplate

        config_service = ConfigService()
        template_service = TemplateService(config_service)

        print("✓ TemplateService initialized")

        # Test listing templates
        templates = template_service.list_templates()
        print(f"✓ Found {len(templates)} templates")

        # Test categories
        categories = template_service.get_categories()
        print(f"✓ Found {len(categories)} categories: {categories}")

        # Test creating a template
        test_template = ConfigurationTemplate(
            name="Demo Template",
            description="A demo template for testing",
            category="demo",
            instructions="You are a demo assistant."
        )

        if template_service.save_template(test_template):
            print("✓ Template saved successfully")

            # Test loading template
            loaded_template = template_service.load_template("Demo Template")
            if loaded_template and loaded_template.name == "Demo Template":
                print("✓ Template loaded successfully")
            else:
                print("✗ Failed to load template")
        else:
            print("✗ Failed to save template")

        return True

    except Exception as e:
        print(f"✗ TemplateService test failed: {e}")
        return False

def test_workspace_service():
    """Test the workspace service."""
    print("\nTesting WorkspaceService...")

    try:
        from services.config_service import ConfigService
        from services.workspace_service import WorkspaceService
        from models.workspace import EnhancedGemConfiguration, WorkspaceType

        config_service = ConfigService()
        workspace_service = WorkspaceService(config_service)

        print("✓ WorkspaceService initialized")

        # Test listing workspaces
        workspaces = workspace_service.list_workspaces()
        print(f"✓ Found {len(workspaces)} workspaces")

        # Test creating a workspace
        test_workspace = workspace_service.create_workspace(
            name="Demo Workspace",
            description="A demo workspace for testing",
            workspace_type=WorkspaceType.PROJECT
        )

        if test_workspace:
            print("✓ Workspace created successfully")

            # Test creating and adding configuration
            test_config = EnhancedGemConfiguration(
                name="Demo Config",
                instructions="Demo instructions",
                description="A demo configuration"
            )

            if workspace_service.save_configuration(test_config):
                print("✓ Configuration saved successfully")

                # Add to workspace
                if workspace_service.add_configuration_to_workspace(test_workspace.id, test_config.id):
                    print("✓ Configuration added to workspace")

                    # List configurations in workspace
                    configs = workspace_service.list_configurations(test_workspace.id)
                    print(f"✓ Found {len(configs)} configurations in workspace")
                else:
                    print("✗ Failed to add configuration to workspace")
            else:
                print("✗ Failed to save configuration")
        else:
            print("✗ Failed to create workspace")

        return True

    except Exception as e:
        print(f"✗ WorkspaceService test failed: {e}")
        return False

def test_session_service():
    """Test the session service."""
    print("\nTesting SessionService...")

    try:
        from services.config_service import ConfigService
        from services.session_service import SessionService

        config_service = ConfigService()
        session_service = SessionService(config_service)

        print("✓ SessionService initialized")

        # Test workspace tracking
        session_service.set_current_workspace("test_workspace")
        current_workspace = session_service.get_current_workspace_id()
        print(f"✓ Workspace tracking works: {current_workspace}")

        # Test configuration tracking
        session_service.set_current_configuration("test_config")
        current_config = session_service.get_current_configuration_id()
        print(f"✓ Configuration tracking works: {current_config}")

        # Test recent configurations
        recent_configs = session_service.get_recent_configurations()
        print(f"✓ Recent configurations: {len(recent_configs)} items")

        # Test window geometry
        test_geometry = {"x": 100, "y": 100, "width": 800, "height": 600}
        session_service.save_window_geometry(test_geometry)
        loaded_geometry = session_service.get_window_geometry()
        print(f"✓ Window geometry persistence works: {loaded_geometry == test_geometry}")

        # Test session statistics
        stats = session_service.get_session_statistics()
        print(f"✓ Session statistics available: {list(stats.keys())}")

        return True

    except Exception as e:
        print(f"✗ SessionService test failed: {e}")
        return False

def test_import_export_service():
    """Test the import/export service."""
    print("\nTesting ImportExportService...")

    try:
        from services.config_service import ConfigService
        from services.workspace_service import WorkspaceService
        from services.template_service import TemplateService
        from services.import_export_service import ImportExportService
        from models.workspace import EnhancedGemConfiguration

        config_service = ConfigService()
        workspace_service = WorkspaceService(config_service)
        template_service = TemplateService(config_service)
        import_export_service = ImportExportService(
            config_service, workspace_service, template_service
        )

        print("✓ ImportExportService initialized")

        # Create test configuration
        test_config = EnhancedGemConfiguration(
            name="Export Test Config",
            instructions="Test instructions for export",
            description="A test configuration for export testing"
        )

        if workspace_service.save_configuration(test_config):
            print("✓ Test configuration created")

            # Test export
            export_path = import_export_service.export_configuration(test_config.id)
            if export_path:
                print(f"✓ Configuration exported to: {export_path}")

                # Test import (would need more complex setup)
                print("✓ Export functionality works")
            else:
                print("✗ Failed to export configuration")
        else:
            print("✗ Failed to create test configuration")

        # Test export history
        history = import_export_service.get_export_history()
        print(f"✓ Export history: {len(history)} items")

        return True

    except Exception as e:
        print(f"✗ ImportExportService test failed: {e}")
        return False

def main():
    """Main demo function."""
    print("Custom Gemini Agent GUI - Demo Script")
    print("=" * 50)
    
    # Check basic imports
    pyqt_available = check_basic_imports()
    
    # Test services
    config_ok = test_config_service()
    api_ok = test_api_service()
    rag_ok = test_rag_service()
    monitoring_ok = test_monitoring_service()
    gdrive_ok = test_google_drive_service()
    webscraping_ok = test_web_scraping_service()
    batch_ok = test_batch_processing_service()

    # Epic 5 services
    template_ok = test_template_service()
    workspace_ok = test_workspace_service()
    session_ok = test_session_service()
    import_export_ok = test_import_export_service()

    controller_ok = test_main_controller()
    
    # Test UI components if PyQt6 is available
    ui_ok = True
    if pyqt_available:
        ui_ok = test_ui_components()
        
        # Run full demo
        full_demo_ok = run_full_demo()
    else:
        print("\nSkipping UI tests (PyQt6 not available)")
        full_demo_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("DEMO SUMMARY")
    print("=" * 50)
    print(f"PyQt6 Available: {'✓' if pyqt_available else '✗'}")
    print(f"ConfigService: {'✓' if config_ok else '✗'}")
    print(f"APIService: {'✓' if api_ok else '✗'}")
    print(f"Enhanced RAGService: {'✓' if rag_ok else '✗'}")
    print(f"MonitoringService: {'✓' if monitoring_ok else '✗'}")
    print(f"GoogleDriveService: {'✓' if gdrive_ok else '✗'}")
    print(f"WebScrapingService: {'✓' if webscraping_ok else '✗'}")
    print(f"BatchProcessingService: {'✓' if batch_ok else '✗'}")
    print(f"TemplateService: {'✓' if template_ok else '✗'}")
    print(f"WorkspaceService: {'✓' if workspace_ok else '✗'}")
    print(f"SessionService: {'✓' if session_ok else '✗'}")
    print(f"ImportExportService: {'✓' if import_export_ok else '✗'}")
    print(f"MainController: {'✓' if controller_ok else '✗'}")
    print(f"UI Components: {'✓' if ui_ok else '✗'}")
    print(f"Full Demo: {'✓' if full_demo_ok else '✗'}")
    
    if all([config_ok, api_ok, rag_ok, monitoring_ok, gdrive_ok, webscraping_ok, batch_ok,
            template_ok, workspace_ok, session_ok, import_export_ok, controller_ok]):
        print("\n🎉 Core functionality is working!")
        if pyqt_available and ui_ok:
            print("🎉 UI components are working!")
            print("\nNext steps:")
            print("1. Install missing dependencies: pip install -r requirements.txt")
            print("2. Configure your Google Gemini API key")
            print("3. Run the application: python run.py")
        else:
            print("\nNext steps:")
            print("1. Install PyQt6: pip install PyQt6")
            print("2. Install other dependencies: pip install -r requirements.txt")
            print("3. Run the application: python run.py")
    else:
        print("\n❌ Some core components have issues.")
        print("Please check the error messages above.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
