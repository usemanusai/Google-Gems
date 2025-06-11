"""
Knowledge Source Model

Data model for representing knowledge sources in the RAG system.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Types of knowledge sources."""
    FILE = "file"
    FOLDER = "folder"
    GITHUB = "github"
    GOOGLE_DRIVE = "google_drive"
    URL = "url"
    WEBSITE = "website"  # For crawled websites
    SITEMAP = "sitemap"  # For sitemap-based extraction


class SourceStatus(str, Enum):
    """Status of knowledge source processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"
    MONITORING = "monitoring"


class KnowledgeSource(BaseModel):
    """Model for a knowledge source."""
    
    id: str = Field(description="Unique identifier for the source")
    path: str = Field(description="Path or URL to the source")
    source_type: SourceType = Field(description="Type of the source")
    status: SourceStatus = Field(default=SourceStatus.PENDING, description="Processing status")
    
    # Metadata
    name: str = Field(description="Display name for the source")
    description: Optional[str] = Field(default=None, description="Optional description")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    indexed_at: Optional[datetime] = Field(default=None, description="Last indexing timestamp")
    
    # Processing info
    file_count: int = Field(default=0, description="Number of files in this source")
    chunk_count: int = Field(default=0, description="Number of text chunks extracted")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Source-specific configuration")
    
    class Config:
        use_enum_values = True
    
    def update_status(self, status: SourceStatus, error_message: Optional[str] = None):
        """Update the source status."""
        self.status = status
        self.updated_at = datetime.now()
        if error_message:
            self.error_message = error_message
        if status == SourceStatus.INDEXED:
            self.indexed_at = datetime.now()
    
    def is_ready(self) -> bool:
        """Check if the source is ready for querying."""
        return self.status == SourceStatus.INDEXED
    
    def is_processing(self) -> bool:
        """Check if the source is currently being processed."""
        return self.status == SourceStatus.PROCESSING
    
    def has_error(self) -> bool:
        """Check if the source has an error."""
        return self.status == SourceStatus.ERROR
    
    def get_display_name(self) -> str:
        """Get a display-friendly name for the source."""
        if self.name:
            return self.name
        
        if self.source_type == SourceType.FILE:
            from pathlib import Path
            return Path(self.path).name
        elif self.source_type == SourceType.FOLDER:
            from pathlib import Path
            return f"Folder: {Path(self.path).name}"
        elif self.source_type == SourceType.GITHUB:
            # Extract repo name from URL
            parts = self.path.rstrip('/').split('/')
            if len(parts) >= 2:
                return f"GitHub: {parts[-2]}/{parts[-1]}"
            return f"GitHub: {self.path}"
        elif self.source_type == SourceType.GOOGLE_DRIVE:
            return f"Google Drive: {self.path}"
        else:
            return self.path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeSource":
        """Create instance from dictionary."""
        return cls(**data)
