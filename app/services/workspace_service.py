"""
Workspace Service

Manages workspaces, multi-workspace support, and workspace operations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from models.workspace import Workspace, WorkspaceType, EnhancedGemConfiguration
from services.config_service import ConfigService


class WorkspaceService:
    """Service for managing workspaces."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.workspaces_dir = config_service.get_app_directory() / "workspaces"
        self.configurations_dir = config_service.get_app_directory() / "configurations"
        
        # Create directories
        self.workspaces_dir.mkdir(exist_ok=True)
        self.configurations_dir.mkdir(exist_ok=True)
        
        # Initialize default workspace
        self._initialize_default_workspace()
    
    def _initialize_default_workspace(self):
        """Initialize the default workspace if it doesn't exist."""
        default_workspace = Workspace(
            id="default",
            name="Default Workspace",
            description="Default workspace for personal configurations",
            workspace_type=WorkspaceType.PERSONAL,
            color="#3498db",
            icon="home"
        )
        
        if not self._workspace_exists("default"):
            self.save_workspace(default_workspace)
            logger.info("Initialized default workspace")
    
    def save_workspace(self, workspace: Workspace) -> bool:
        """Save a workspace to file."""
        try:
            workspace_file = self.workspaces_dir / f"{workspace.id}.json"
            workspace.modified_at = datetime.now()
            
            with open(workspace_file, 'w', encoding='utf-8') as f:
                json.dump(workspace.model_dump(), f, indent=2, default=str)
            logger.info(f"Workspace '{workspace.name}' saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save workspace: {e}")
            return False
    
    def load_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Load a workspace by ID."""
        try:
            workspace_file = self.workspaces_dir / f"{workspace_id}.json"
            if workspace_file.exists():
                with open(workspace_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Workspace(**data)
            else:
                logger.warning(f"Workspace '{workspace_id}' not found")
                return None
        except Exception as e:
            logger.error(f"Failed to load workspace '{workspace_id}': {e}")
            return None
    
    def list_workspaces(self) -> List[Workspace]:
        """List all available workspaces."""
        workspaces = []
        
        try:
            workspace_files = list(self.workspaces_dir.glob("*.json"))
            
            for workspace_file in workspace_files:
                try:
                    with open(workspace_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    workspace = Workspace(**data)
                    workspaces.append(workspace)
                except Exception as e:
                    logger.error(f"Failed to load workspace file {workspace_file}: {e}")
                    continue
            
            # Sort by name
            workspaces.sort(key=lambda w: w.name)
            
        except Exception as e:
            logger.error(f"Failed to list workspaces: {e}")
        
        return workspaces
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        try:
            if workspace_id == "default":
                logger.warning("Cannot delete default workspace")
                return False
            
            workspace_file = self.workspaces_dir / f"{workspace_id}.json"
            if workspace_file.exists():
                workspace_file.unlink()
                logger.info(f"Workspace '{workspace_id}' deleted")
                return True
            else:
                logger.warning(f"Workspace '{workspace_id}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete workspace '{workspace_id}': {e}")
            return False
    
    def create_workspace(self, name: str, description: str = "", 
                        workspace_type: WorkspaceType = WorkspaceType.PERSONAL,
                        color: str = "#3498db", icon: str = "folder") -> Optional[Workspace]:
        """Create a new workspace."""
        try:
            workspace = Workspace(
                name=name,
                description=description,
                workspace_type=workspace_type,
                color=color,
                icon=icon
            )
            
            if self.save_workspace(workspace):
                logger.info(f"Created workspace '{name}'")
                return workspace
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            return None
    
    def save_configuration(self, config: EnhancedGemConfiguration) -> bool:
        """Save an enhanced configuration to file."""
        try:
            config_file = self.configurations_dir / f"{config.id}.json"
            config.modified_at = datetime.now()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(), f, indent=2, default=str)
            logger.info(f"Configuration '{config.name}' saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_configuration(self, config_id: str) -> Optional[EnhancedGemConfiguration]:
        """Load a configuration by ID."""
        try:
            config_file = self.configurations_dir / f"{config_id}.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return EnhancedGemConfiguration(**data)
            else:
                logger.warning(f"Configuration '{config_id}' not found")
                return None
        except Exception as e:
            logger.error(f"Failed to load configuration '{config_id}': {e}")
            return None
    
    def list_configurations(self, workspace_id: Optional[str] = None) -> List[EnhancedGemConfiguration]:
        """List configurations, optionally filtered by workspace."""
        configurations = []
        
        try:
            config_files = list(self.configurations_dir.glob("*.json"))
            
            for config_file in config_files:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    config = EnhancedGemConfiguration(**data)
                    
                    # Filter by workspace if specified
                    if workspace_id is None:
                        configurations.append(config)
                    else:
                        # Check if configuration is in the specified workspace
                        workspace = self.load_workspace(workspace_id)
                        if workspace and config.id in workspace.configurations:
                            configurations.append(config)
                            
                except Exception as e:
                    logger.error(f"Failed to load configuration file {config_file}: {e}")
                    continue
            
            # Sort by last used, then by name
            configurations.sort(key=lambda c: (c.last_used_at or datetime.min, c.name), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list configurations: {e}")
        
        return configurations
    
    def add_configuration_to_workspace(self, workspace_id: str, config_id: str) -> bool:
        """Add a configuration to a workspace."""
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return False
            
            workspace.add_configuration(config_id)
            return self.save_workspace(workspace)
            
        except Exception as e:
            logger.error(f"Failed to add configuration to workspace: {e}")
            return False
    
    def remove_configuration_from_workspace(self, workspace_id: str, config_id: str) -> bool:
        """Remove a configuration from a workspace."""
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return False
            
            workspace.remove_configuration(config_id)
            return self.save_workspace(workspace)
            
        except Exception as e:
            logger.error(f"Failed to remove configuration from workspace: {e}")
            return False
    
    def move_configuration(self, config_id: str, from_workspace_id: str, to_workspace_id: str) -> bool:
        """Move a configuration from one workspace to another."""
        try:
            # Remove from source workspace
            if not self.remove_configuration_from_workspace(from_workspace_id, config_id):
                return False
            
            # Add to target workspace
            return self.add_configuration_to_workspace(to_workspace_id, config_id)
            
        except Exception as e:
            logger.error(f"Failed to move configuration: {e}")
            return False
    
    def duplicate_configuration(self, config_id: str, new_name: str) -> Optional[EnhancedGemConfiguration]:
        """Duplicate a configuration with a new name."""
        try:
            original_config = self.load_configuration(config_id)
            if not original_config:
                return None
            
            # Create new configuration with copied data
            new_config = EnhancedGemConfiguration(
                name=new_name,
                instructions=original_config.instructions,
                knowledge_sources=original_config.knowledge_sources.copy(),
                description=f"Copy of {original_config.name}",
                category=original_config.category,
                tags=original_config.tags.copy(),
                settings=original_config.settings.copy(),
                template_id=original_config.template_id,
                template_version=original_config.template_version
            )
            
            if self.save_configuration(new_config):
                logger.info(f"Duplicated configuration '{original_config.name}' as '{new_name}'")
                return new_config
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to duplicate configuration: {e}")
            return None
    
    def search_configurations(self, query: str, workspace_id: Optional[str] = None) -> List[EnhancedGemConfiguration]:
        """Search configurations by name, description, or tags."""
        configurations = self.list_configurations(workspace_id)
        query_lower = query.lower()
        
        matching_configs = []
        
        for config in configurations:
            # Search in name, description, instructions, and tags
            if (query_lower in config.name.lower() or
                query_lower in config.description.lower() or
                query_lower in config.instructions.lower() or
                any(query_lower in tag.lower() for tag in config.tags)):
                matching_configs.append(config)
        
        return matching_configs
    
    def get_workspace_statistics(self, workspace_id: str) -> Dict[str, Any]:
        """Get statistics for a workspace."""
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return {}
            
            configurations = self.list_configurations(workspace_id)
            
            total_messages = sum(config.total_messages for config in configurations)
            total_usage = sum(config.usage_count for config in configurations)
            
            # Get categories
            categories = list(set(config.category for config in configurations))
            
            # Get most used configuration
            most_used = max(configurations, key=lambda c: c.usage_count) if configurations else None
            
            return {
                "total_configurations": len(configurations),
                "total_messages": total_messages,
                "total_usage": total_usage,
                "categories": categories,
                "most_used_config": most_used.name if most_used else None,
                "created_at": workspace.created_at,
                "modified_at": workspace.modified_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get workspace statistics: {e}")
            return {}
    
    def _workspace_exists(self, workspace_id: str) -> bool:
        """Check if a workspace exists."""
        workspace_file = self.workspaces_dir / f"{workspace_id}.json"
        return workspace_file.exists()
