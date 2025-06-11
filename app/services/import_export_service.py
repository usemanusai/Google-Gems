"""
Import/Export Service

Handles import and export of configurations, workspaces, and templates.
"""

import json
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from loguru import logger

from models.workspace import ConfigurationExport, EnhancedGemConfiguration, Workspace, ConfigurationTemplate
from services.config_service import ConfigService
from services.workspace_service import WorkspaceService
from services.template_service import TemplateService


class ImportExportService:
    """Service for import/export operations."""
    
    def __init__(self, config_service: ConfigService, workspace_service: WorkspaceService, 
                 template_service: TemplateService):
        self.config_service = config_service
        self.workspace_service = workspace_service
        self.template_service = template_service
        
        self.export_dir = config_service.get_app_directory() / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def export_configuration(self, config_id: str, include_knowledge_sources: bool = True) -> Optional[str]:
        """Export a single configuration to JSON file."""
        try:
            config = self.workspace_service.load_configuration(config_id)
            if not config:
                logger.error(f"Configuration {config_id} not found")
                return None
            
            # Create export data
            export_data = ConfigurationExport(
                configurations=[config],
                include_knowledge_sources=include_knowledge_sources
            )
            
            # Generate filename
            safe_name = config.name.replace(" ", "_").replace("/", "_")
            filename = f"config_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = self.export_dir / filename
            
            # Save export file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Exported configuration '{config.name}' to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return None
    
    def export_workspace(self, workspace_id: str, include_configurations: bool = True,
                        include_knowledge_sources: bool = True) -> Optional[str]:
        """Export a workspace and its configurations."""
        try:
            workspace = self.workspace_service.load_workspace(workspace_id)
            if not workspace:
                logger.error(f"Workspace {workspace_id} not found")
                return None
            
            configurations = []
            if include_configurations:
                for config_id in workspace.configurations:
                    config = self.workspace_service.load_configuration(config_id)
                    if config:
                        configurations.append(config)
            
            # Create export data
            export_data = ConfigurationExport(
                workspaces=[workspace],
                configurations=configurations,
                include_knowledge_sources=include_knowledge_sources
            )
            
            # Generate filename
            safe_name = workspace.name.replace(" ", "_").replace("/", "_")
            filename = f"workspace_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = self.export_dir / filename
            
            # Save export file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Exported workspace '{workspace.name}' to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Failed to export workspace: {e}")
            return None
    
    def export_multiple(self, config_ids: List[str] = None, workspace_ids: List[str] = None,
                       template_names: List[str] = None, include_knowledge_sources: bool = True) -> Optional[str]:
        """Export multiple items to a single file."""
        try:
            configurations = []
            workspaces = []
            templates = []
            
            # Collect configurations
            if config_ids:
                for config_id in config_ids:
                    config = self.workspace_service.load_configuration(config_id)
                    if config:
                        configurations.append(config)
            
            # Collect workspaces
            if workspace_ids:
                for workspace_id in workspace_ids:
                    workspace = self.workspace_service.load_workspace(workspace_id)
                    if workspace:
                        workspaces.append(workspace)
            
            # Collect templates
            if template_names:
                for template_name in template_names:
                    template = self.template_service.load_template(template_name)
                    if template:
                        templates.append(template)
            
            # Create export data
            export_data = ConfigurationExport(
                configurations=configurations,
                workspaces=workspaces,
                templates=templates,
                include_knowledge_sources=include_knowledge_sources
            )
            
            # Generate filename
            filename = f"multi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = self.export_dir / filename
            
            # Save export file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Exported multiple items to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Failed to export multiple items: {e}")
            return None
    
    def create_backup(self, include_knowledge_sources: bool = False) -> Optional[str]:
        """Create a complete backup of all data."""
        try:
            # Get all data
            all_workspaces = self.workspace_service.list_workspaces()
            all_configurations = self.workspace_service.list_configurations()
            all_templates = self.template_service.list_templates()
            
            # Create export data
            export_data = ConfigurationExport(
                configurations=all_configurations,
                workspaces=all_workspaces,
                templates=all_templates,
                include_knowledge_sources=include_knowledge_sources
            )
            
            # Generate filename
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.export_dir / filename
            
            # Save backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(export_data.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Created backup at {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def import_from_file(self, file_path: str, merge_mode: str = "skip") -> Dict[str, Any]:
        """Import data from a file.
        
        Args:
            file_path: Path to the import file
            merge_mode: How to handle conflicts ("skip", "overwrite", "rename")
        
        Returns:
            Dictionary with import results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate import data
            if not isinstance(data, dict):
                raise ValueError("Invalid import file format")
            
            export_data = ConfigurationExport(**data)
            
            results = {
                "configurations": {"imported": 0, "skipped": 0, "errors": 0},
                "workspaces": {"imported": 0, "skipped": 0, "errors": 0},
                "templates": {"imported": 0, "skipped": 0, "errors": 0},
                "errors": []
            }
            
            # Import templates first
            for template_data in export_data.templates:
                try:
                    template = ConfigurationTemplate(**template_data)
                    
                    if self._handle_template_conflict(template, merge_mode):
                        if self.template_service.save_template(template):
                            results["templates"]["imported"] += 1
                        else:
                            results["templates"]["errors"] += 1
                    else:
                        results["templates"]["skipped"] += 1
                        
                except Exception as e:
                    results["templates"]["errors"] += 1
                    results["errors"].append(f"Template import error: {e}")
            
            # Import workspaces
            for workspace_data in export_data.workspaces:
                try:
                    workspace = Workspace(**workspace_data)
                    
                    if self._handle_workspace_conflict(workspace, merge_mode):
                        if self.workspace_service.save_workspace(workspace):
                            results["workspaces"]["imported"] += 1
                        else:
                            results["workspaces"]["errors"] += 1
                    else:
                        results["workspaces"]["skipped"] += 1
                        
                except Exception as e:
                    results["workspaces"]["errors"] += 1
                    results["errors"].append(f"Workspace import error: {e}")
            
            # Import configurations
            for config_data in export_data.configurations:
                try:
                    config = EnhancedGemConfiguration(**config_data)
                    
                    if self._handle_configuration_conflict(config, merge_mode):
                        if self.workspace_service.save_configuration(config):
                            results["configurations"]["imported"] += 1
                        else:
                            results["configurations"]["errors"] += 1
                    else:
                        results["configurations"]["skipped"] += 1
                        
                except Exception as e:
                    results["configurations"]["errors"] += 1
                    results["errors"].append(f"Configuration import error: {e}")
            
            logger.info(f"Import completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to import from file: {e}")
            return {"error": str(e)}
    
    def _handle_configuration_conflict(self, config: EnhancedGemConfiguration, merge_mode: str) -> bool:
        """Handle configuration name conflicts during import."""
        existing_config = self.workspace_service.load_configuration(config.id)
        
        if not existing_config:
            return True  # No conflict
        
        if merge_mode == "skip":
            return False
        elif merge_mode == "overwrite":
            return True
        elif merge_mode == "rename":
            # Find a unique name
            base_name = config.name
            counter = 1
            while self._configuration_name_exists(config.name):
                config.name = f"{base_name} ({counter})"
                counter += 1
            return True
        
        return False
    
    def _handle_workspace_conflict(self, workspace: Workspace, merge_mode: str) -> bool:
        """Handle workspace conflicts during import."""
        existing_workspace = self.workspace_service.load_workspace(workspace.id)
        
        if not existing_workspace:
            return True  # No conflict
        
        if merge_mode == "skip":
            return False
        elif merge_mode == "overwrite":
            return True
        elif merge_mode == "rename":
            # Find a unique name
            base_name = workspace.name
            counter = 1
            while self._workspace_name_exists(workspace.name):
                workspace.name = f"{base_name} ({counter})"
                counter += 1
            return True
        
        return False
    
    def _handle_template_conflict(self, template: ConfigurationTemplate, merge_mode: str) -> bool:
        """Handle template conflicts during import."""
        existing_template = self.template_service.load_template(template.name)
        
        if not existing_template:
            return True  # No conflict
        
        if merge_mode == "skip":
            return False
        elif merge_mode == "overwrite":
            return True
        elif merge_mode == "rename":
            # Find a unique name
            base_name = template.name
            counter = 1
            while self.template_service.load_template(template.name):
                template.name = f"{base_name} ({counter})"
                counter += 1
            return True
        
        return False
    
    def _configuration_name_exists(self, name: str) -> bool:
        """Check if a configuration name exists."""
        configs = self.workspace_service.list_configurations()
        return any(config.name == name for config in configs)
    
    def _workspace_name_exists(self, name: str) -> bool:
        """Check if a workspace name exists."""
        workspaces = self.workspace_service.list_workspaces()
        return any(workspace.name == name for workspace in workspaces)
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get list of export files."""
        try:
            export_files = []
            
            for file_path in self.export_dir.glob("*.json"):
                try:
                    stat = file_path.stat()
                    export_files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime),
                        "modified": datetime.fromtimestamp(stat.st_mtime)
                    })
                except Exception as e:
                    logger.error(f"Error reading export file {file_path}: {e}")
                    continue
            
            # Sort by creation time, newest first
            export_files.sort(key=lambda x: x["created"], reverse=True)
            return export_files
            
        except Exception as e:
            logger.error(f"Failed to get export history: {e}")
            return []
