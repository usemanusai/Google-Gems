"""
Workspace Model

Enhanced workspace and configuration management models for Epic 5.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class WorkspaceType(str, Enum):
    """Types of workspaces."""
    PERSONAL = "personal"
    TEAM = "team"
    PROJECT = "project"
    TEMPLATE = "template"


class ConfigurationTemplate(BaseModel):
    """Model for configuration templates."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(description="Template name")
    description: str = Field(default="", description="Template description")
    category: str = Field(default="general", description="Template category")
    instructions: str = Field(description="Default instructions")
    default_knowledge_sources: List[Dict[str, Any]] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="user")
    version: str = Field(default="1.0.0")
    is_builtin: bool = Field(default=False)
    
    class Config:
        use_enum_values = True


class EnhancedGemConfiguration(BaseModel):
    """Enhanced Gem configuration with additional metadata."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(description="Configuration name")
    instructions: str = Field(default="", description="Agent instructions")
    knowledge_sources: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Enhanced metadata
    description: str = Field(default="", description="Configuration description")
    category: str = Field(default="general", description="Configuration category")
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = Field(default=None)
    
    # Usage statistics
    usage_count: int = Field(default=0)
    total_messages: int = Field(default=0)
    
    # Configuration settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Template information
    template_id: Optional[str] = Field(default=None)
    template_version: Optional[str] = Field(default=None)
    
    # Sharing and collaboration
    is_shared: bool = Field(default=False)
    shared_with: List[str] = Field(default_factory=list)
    permissions: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
    
    def update_usage(self):
        """Update usage statistics."""
        self.usage_count += 1
        self.last_used_at = datetime.now()
        self.modified_at = datetime.now()
    
    def add_message(self):
        """Increment message count."""
        self.total_messages += 1
        self.modified_at = datetime.now()


class Workspace(BaseModel):
    """Model for workspaces."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(description="Workspace name")
    description: str = Field(default="", description="Workspace description")
    workspace_type: WorkspaceType = Field(default=WorkspaceType.PERSONAL)
    
    # Configurations in this workspace
    configurations: List[str] = Field(default_factory=list)  # Configuration IDs
    
    # Workspace settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="user")
    
    # Sharing and collaboration
    is_shared: bool = Field(default=False)
    shared_with: List[str] = Field(default_factory=list)
    permissions: Dict[str, str] = Field(default_factory=dict)
    
    # Organization
    tags: List[str] = Field(default_factory=list)
    color: str = Field(default="#3498db")
    icon: str = Field(default="folder")
    
    class Config:
        use_enum_values = True
    
    def add_configuration(self, config_id: str):
        """Add a configuration to this workspace."""
        if config_id not in self.configurations:
            self.configurations.append(config_id)
            self.modified_at = datetime.now()
    
    def remove_configuration(self, config_id: str):
        """Remove a configuration from this workspace."""
        if config_id in self.configurations:
            self.configurations.remove(config_id)
            self.modified_at = datetime.now()


class ConfigurationExport(BaseModel):
    """Model for configuration export/import."""
    version: str = Field(default="1.0.0")
    export_date: datetime = Field(default_factory=datetime.now)
    exported_by: str = Field(default="user")
    
    # Exported data
    configurations: List[EnhancedGemConfiguration] = Field(default_factory=list)
    templates: List[ConfigurationTemplate] = Field(default_factory=list)
    workspaces: List[Workspace] = Field(default_factory=list)
    
    # Export metadata
    include_knowledge_sources: bool = Field(default=True)
    include_settings: bool = Field(default=True)
    include_usage_stats: bool = Field(default=False)
    
    class Config:
        use_enum_values = True


class SessionState(BaseModel):
    """Model for session state management."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    
    # Current state
    current_workspace_id: Optional[str] = Field(default=None)
    current_configuration_id: Optional[str] = Field(default=None)
    
    # UI state
    window_geometry: Dict[str, int] = Field(default_factory=dict)
    panel_states: Dict[str, bool] = Field(default_factory=dict)
    recent_configurations: List[str] = Field(default_factory=list)
    
    # Chat state
    chat_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    last_active_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_active_at = datetime.now()
    
    def add_recent_configuration(self, config_id: str, max_recent: int = 10):
        """Add a configuration to recent list."""
        if config_id in self.recent_configurations:
            self.recent_configurations.remove(config_id)
        
        self.recent_configurations.insert(0, config_id)
        
        # Limit the number of recent configurations
        if len(self.recent_configurations) > max_recent:
            self.recent_configurations = self.recent_configurations[:max_recent]
        
        self.update_activity()
