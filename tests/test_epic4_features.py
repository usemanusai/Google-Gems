"""
Tests for Epic 4: Advanced Knowledge Ingestion Methods
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

from services.google_drive_service import GoogleDriveService
from services.web_scraping_service import WebScrapingService
from services.batch_processing_service import BatchProcessingService, BatchJob, BatchJobStatus
from services.config_service import ConfigService
from models.knowledge_source import KnowledgeSource, SourceType


class TestGoogleDriveService:
    """Test cases for Google Drive service."""
    
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
    def google_drive_service(self, config_service):
        """Create a GoogleDriveService instance."""
        return GoogleDriveService(config_service)
    
    def test_google_drive_service_initialization(self, google_drive_service):
        """Test Google Drive service initialization."""
        assert google_drive_service is not None
        assert google_drive_service.config_service is not None
        assert not google_drive_service.is_authenticated()
    
    def test_get_extension_from_mime_type(self, google_drive_service):
        """Test MIME type to extension conversion."""
        assert google_drive_service._get_extension_from_mime_type('text/plain') == '.txt'
        assert google_drive_service._get_extension_from_mime_type('application/pdf') == '.pdf'
        assert google_drive_service._get_extension_from_mime_type('text/x-python') == '.py'
        assert google_drive_service._get_extension_from_mime_type('unknown/type') == '.txt'
    
    def test_get_folder_info_invalid_url(self, google_drive_service):
        """Test folder info extraction with invalid URL."""
        result = google_drive_service.get_folder_info("invalid_url")
        assert result is None
    
    def test_extract_text_content_text_file(self, google_drive_service):
        """Test text content extraction from text files."""
        file_data = {
            "content": b"Hello, world!",
            "extension": ".txt"
        }
        
        result = google_drive_service._extract_text_content(file_data)
        assert result == "Hello, world!"
    
    def test_extract_text_content_unsupported_format(self, google_drive_service):
        """Test text content extraction from unsupported format."""
        file_data = {
            "content": b"binary data",
            "extension": ".unknown"
        }
        
        result = google_drive_service._extract_text_content(file_data)
        assert result == "binary data"  # Falls back to text decoding


class TestWebScrapingService:
    """Test cases for web scraping service."""
    
    @pytest.fixture
    def web_scraping_service(self):
        """Create a WebScrapingService instance."""
        return WebScrapingService()
    
    def test_web_scraping_service_initialization(self, web_scraping_service):
        """Test web scraping service initialization."""
        assert web_scraping_service is not None
        assert web_scraping_service.user_agent is not None
    
    def test_is_available(self, web_scraping_service):
        """Test availability check."""
        # This will depend on whether dependencies are installed
        available = web_scraping_service.is_available()
        assert isinstance(available, bool)
    
    @patch('services.web_scraping_service.REQUESTS_AVAILABLE', True)
    @patch('services.web_scraping_service.BEAUTIFULSOUP_AVAILABLE', True)
    def test_extract_with_beautifulsoup(self, web_scraping_service):
        """Test content extraction with BeautifulSoup."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <main>
                    <h1>Main Content</h1>
                    <p>This is the main content of the page.</p>
                </main>
                <script>console.log('script');</script>
            </body>
        </html>
        """
        
        with patch('services.web_scraping_service.BeautifulSoup') as mock_bs:
            # Mock BeautifulSoup behavior
            mock_soup = MagicMock()
            mock_bs.return_value = mock_soup
            
            # Mock title
            mock_title = MagicMock()
            mock_title.get_text.return_value = "Test Page"
            mock_soup.find.return_value = mock_title
            
            # Mock main content
            mock_main = MagicMock()
            mock_main.get_text.return_value = "Main Content This is the main content of the page."
            mock_soup.find.return_value = mock_main
            
            result = web_scraping_service._extract_with_beautifulsoup(html, "http://example.com")
            
            assert result is not None
            assert "method" in result
            assert result["method"] == "beautifulsoup"
    
    def test_validate_url_without_requests(self, web_scraping_service):
        """Test URL validation when requests is not available."""
        with patch('services.web_scraping_service.REQUESTS_AVAILABLE', False):
            result = web_scraping_service.validate_url("http://example.com")
            assert result is False


class TestBatchProcessingService:
    """Test cases for batch processing service."""
    
    @pytest.fixture
    def mock_rag_service(self):
        """Create a mock RAG service."""
        mock_service = MagicMock()
        mock_service.process_knowledge_source.return_value = True
        return mock_service
    
    @pytest.fixture
    def batch_processing_service(self, mock_rag_service):
        """Create a BatchProcessingService instance."""
        return BatchProcessingService(mock_rag_service)
    
    def test_batch_processing_service_initialization(self, batch_processing_service):
        """Test batch processing service initialization."""
        assert batch_processing_service is not None
        assert not batch_processing_service.is_processing()
        assert batch_processing_service.max_workers == 3
    
    def test_set_max_workers(self, batch_processing_service):
        """Test setting maximum workers."""
        batch_processing_service.set_max_workers(5)
        assert batch_processing_service.max_workers == 5
    
    def test_batch_job_creation(self):
        """Test batch job creation."""
        source = KnowledgeSource(
            id="test_source",
            path="/test/path",
            source_type=SourceType.FILE,
            name="Test Source"
        )
        
        job = BatchJob(id="test_job", source=source)
        
        assert job.id == "test_job"
        assert job.source == source
        assert job.status == BatchJobStatus.PENDING
        assert job.progress == 0.0
        assert job.error_message is None
    
    def test_get_processing_statistics_empty(self, batch_processing_service):
        """Test getting statistics when no jobs exist."""
        stats = batch_processing_service.get_processing_statistics()
        
        assert stats["total"] == 0
        assert stats["status_counts"] == {}
        assert stats["is_processing"] is False
    
    def test_clear_completed_jobs(self, batch_processing_service):
        """Test clearing completed jobs."""
        # Add some mock jobs
        source = KnowledgeSource(
            id="test_source",
            path="/test/path",
            source_type=SourceType.FILE,
            name="Test Source"
        )
        
        job1 = BatchJob(id="job1", source=source)
        job1.status = BatchJobStatus.COMPLETED
        
        job2 = BatchJob(id="job2", source=source)
        job2.status = BatchJobStatus.PENDING
        
        batch_processing_service.current_jobs = {"job1": job1, "job2": job2}
        
        # Clear completed jobs
        batch_processing_service.clear_completed_jobs()
        
        # Only pending job should remain
        assert len(batch_processing_service.current_jobs) == 1
        assert "job2" in batch_processing_service.current_jobs
        assert "job1" not in batch_processing_service.current_jobs


class TestAdvancedIngestionIntegration:
    """Integration tests for advanced ingestion methods."""
    
    def test_source_type_enum_completeness(self):
        """Test that all source types are properly defined."""
        expected_types = [
            "file", "folder", "github", "google_drive", 
            "url", "website", "sitemap"
        ]
        
        actual_types = [source_type.value for source_type in SourceType]
        
        for expected in expected_types:
            assert expected in actual_types
    
    def test_knowledge_source_with_config(self):
        """Test KnowledgeSource with configuration."""
        config = {
            "crawl_mode": "crawl",
            "max_pages": 10,
            "same_domain_only": True
        }
        
        source = KnowledgeSource(
            id="test_url_source",
            path="https://example.com",
            source_type=SourceType.URL,
            name="Example Website",
            config=config
        )
        
        assert source.config == config
        assert source.source_type == SourceType.URL
        assert source.path == "https://example.com"


if __name__ == "__main__":
    pytest.main([__file__])
