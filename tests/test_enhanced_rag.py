"""
Tests for Enhanced RAG Service (Epic 3)
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

from services.rag_service import RAGService
from services.config_service import ConfigService
from services.monitoring_service import MonitoringService
from models.knowledge_source import KnowledgeSource, SourceType, SourceStatus


class TestEnhancedRAGService:
    """Test cases for enhanced RAG service functionality."""
    
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
    def rag_service(self, config_service):
        """Create a RAGService instance."""
        return RAGService(config_service)
    
    def test_smart_chunking_code_files(self, rag_service):
        """Test smart chunking for code files."""
        # Mock document with Python code
        doc = {
            "content": """
def function1():
    return "hello"

class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        return 42

def function2():
    return "world"
""",
            "metadata": {"file_type": ".py"}
        }
        
        chunks = rag_service._smart_chunk_document(doc)
        
        # Should use code splitter
        assert len(chunks) > 0
        assert isinstance(chunks, list)
    
    def test_determine_chunk_type(self, rag_service):
        """Test chunk type determination."""
        assert rag_service._determine_chunk_type(".py") == "code"
        assert rag_service._determine_chunk_type(".js") == "code"
        assert rag_service._determine_chunk_type(".md") == "documentation"
        assert rag_service._determine_chunk_type(".pdf") == "document"
        assert rag_service._determine_chunk_type(".json") == "data"
        assert rag_service._determine_chunk_type(".txt") == "documentation"
    
    def test_enhanced_search_with_filtering(self, rag_service):
        """Test enhanced search with content type filtering."""
        # Mock the collection and embedding model
        with patch.object(rag_service, '_is_rag_available', return_value=True):
            with patch.object(rag_service, 'collection') as mock_collection:
                with patch.object(rag_service, 'embedding_model') as mock_embedding:
                    
                    # Setup mocks
                    mock_embedding.encode.return_value = [[0.1, 0.2, 0.3]]
                    mock_collection.query.return_value = {
                        "documents": [["test content"]],
                        "metadatas": [[{"chunk_type": "code", "source_id": "test"}]],
                        "distances": [[0.5]]
                    }
                    
                    # Test search with content type filter
                    results = rag_service.search_similar(
                        "test query", 
                        content_type="code"
                    )
                    
                    # Verify filtering was applied
                    mock_collection.query.assert_called_once()
                    call_args = mock_collection.query.call_args
                    assert "where" in call_args[1]
                    assert call_args[1]["where"]["chunk_type"] == "code"
                    
                    # Verify results format
                    assert len(results) == 1
                    assert "relevance_score" in results[0]
                    assert "similarity" in results[0]
    
    def test_relevance_score_calculation(self, rag_service):
        """Test relevance score calculation."""
        query = "python function code"
        content = "def my_function(): return 'hello world'"
        metadata = {"chunk_type": "code", "source_id": "test"}
        base_similarity = 0.8
        
        score = rag_service._calculate_relevance_score(
            query, content, metadata, base_similarity
        )
        
        # Should boost score for code content type and keyword overlap
        assert score > base_similarity
        assert score <= 1.0
    
    def test_batch_processing(self, rag_service):
        """Test batch processing of chunks."""
        # Create mock chunks
        chunks = [
            {
                "content": f"Test content {i}",
                "metadata": {"chunk_index": i, "source_id": "test"}
            }
            for i in range(150)  # More than batch size
        ]
        
        with patch.object(rag_service, '_is_rag_available', return_value=True):
            with patch.object(rag_service, 'collection') as mock_collection:
                with patch.object(rag_service, 'embedding_model') as mock_embedding:
                    
                    # Mock embedding generation
                    mock_embedding.encode.return_value = [[0.1, 0.2, 0.3]] * 100
                    
                    # Test batch processing
                    rag_service._store_chunks(chunks, "test_source")
                    
                    # Should be called multiple times for batches
                    assert mock_collection.add.call_count >= 2


class TestMonitoringService:
    """Test cases for file monitoring service."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def monitoring_service(self):
        """Create a MonitoringService instance."""
        return MonitoringService()
    
    def test_monitoring_service_initialization(self, monitoring_service):
        """Test monitoring service initialization."""
        assert monitoring_service is not None
        assert not monitoring_service.is_monitoring
        assert len(monitoring_service.monitored_sources) == 0
    
    def test_add_file_monitoring(self, monitoring_service, temp_dir):
        """Test adding file monitoring."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Create knowledge source
        source = KnowledgeSource(
            id="test_source",
            path=str(test_file),
            source_type=SourceType.FILE,
            name="Test File"
        )
        
        # Mock watchdog availability
        with patch('services.monitoring_service.WATCHDOG_AVAILABLE', True):
            with patch.object(monitoring_service, 'observer') as mock_observer:
                mock_observer.schedule.return_value = "mock_watch"
                
                # Test adding monitoring
                result = monitoring_service.add_source_monitoring(source)
                
                # Should succeed
                assert result is True
                assert source.id in monitoring_service.monitored_sources
                assert source.status == SourceStatus.MONITORING
    
    def test_monitoring_without_watchdog(self, monitoring_service, temp_dir):
        """Test monitoring behavior when watchdog is not available."""
        # Create knowledge source
        source = KnowledgeSource(
            id="test_source",
            path=str(temp_dir / "test.txt"),
            source_type=SourceType.FILE,
            name="Test File"
        )
        
        # Mock watchdog not available
        with patch('services.monitoring_service.WATCHDOG_AVAILABLE', False):
            result = monitoring_service.add_source_monitoring(source)
            
            # Should fail gracefully
            assert result is False
    
    def test_get_monitored_sources(self, monitoring_service):
        """Test getting monitored sources information."""
        # Add mock monitored source
        mock_source = KnowledgeSource(
            id="test_source",
            path="/test/path",
            source_type=SourceType.FILE,
            name="Test Source"
        )
        
        monitoring_service.monitored_sources["test_source"] = {
            "source": mock_source,
            "path": "/test/path",
            "file_filter": None
        }
        
        sources_info = monitoring_service.get_monitored_sources()
        
        assert "test_source" in sources_info
        assert sources_info["test_source"]["source_name"] == "Test Source"
        assert sources_info["test_source"]["path"] == "/test/path"


if __name__ == "__main__":
    pytest.main([__file__])
