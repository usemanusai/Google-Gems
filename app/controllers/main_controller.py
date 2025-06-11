"""
Main Controller

Coordinates between the UI and business logic services.
Implements the Controller part of the MVC pattern.
"""

import asyncio
from typing import Optional, List, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from loguru import logger

from services.config_service import ConfigService, GemConfiguration
from services.api_service import APIService
from services.rag_service import RAGService
from services.monitoring_service import MonitoringService
from services.batch_processing_service import BatchProcessingService
from services.template_service import TemplateService
from services.workspace_service import WorkspaceService
from services.import_export_service import ImportExportService
from services.session_service import SessionService
from models.knowledge_source import KnowledgeSource, SourceType
from models.workspace import EnhancedGemConfiguration, Workspace, ConfigurationTemplate


class MainController(QObject):
    """Main application controller."""
    
    # Signals
    message_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    knowledge_source_processed = pyqtSignal(str)  # source_id
    knowledge_source_updated = pyqtSignal(str, str)  # source_id, event_type
    monitoring_status_changed = pyqtSignal(str, bool)  # source_id, is_monitoring
    batch_processing_started = pyqtSignal(int)  # total_jobs
    batch_processing_completed = pyqtSignal(int, int)  # successful, total
    google_drive_auth_needed = pyqtSignal()

    # Epic 5 signals
    workspace_changed = pyqtSignal(str)  # workspace_id
    configuration_created = pyqtSignal(str)  # config_id
    template_applied = pyqtSignal(str, str)  # template_name, config_name
    import_completed = pyqtSignal(dict)  # import_results
    export_completed = pyqtSignal(str)  # export_path
    
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.config_service = ConfigService()
        self.api_service = APIService(self.config_service)
        self.rag_service = RAGService(self.config_service)
        self.monitoring_service = MonitoringService()
        self.batch_processing_service = BatchProcessingService(self.rag_service)

        # Epic 5 services
        self.template_service = TemplateService(self.config_service)
        self.workspace_service = WorkspaceService(self.config_service)
        self.import_export_service = ImportExportService(
            self.config_service, self.workspace_service, self.template_service
        )
        self.session_service = SessionService(self.config_service)
        
        # Current state
        self.current_gem_config: Optional[EnhancedGemConfiguration] = None
        self.knowledge_sources: List[KnowledgeSource] = []
        self.current_workspace_id: str = "default"
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(self.config_service.settings.auto_save_interval * 1000)

        # Connect monitoring service signals
        self.monitoring_service.file_changed.connect(self.on_file_changed)
        self.monitoring_service.monitoring_error.connect(self.on_monitoring_error)

        # Connect batch processing signals
        self.batch_processing_service.batch_started.connect(self.batch_processing_started)
        self.batch_processing_service.batch_completed.connect(self.batch_processing_completed)

        logger.info("MainController initialized")
    
    def initialize(self) -> bool:
        """Initialize the controller and services."""
        try:
            # Configure API service
            if not self.api_service.configure_api():
                logger.warning("API service not configured - API key may be missing")
            
            # Load last gem configuration if available
            last_gem = self.config_service.settings.last_gem_config
            if last_gem:
                self.load_gem_configuration(last_gem)

            # Start monitoring service
            if self.monitoring_service.start_monitoring():
                logger.info("File monitoring service started")

            self.status_updated.emit("Ready")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize controller: {e}")
            self.error_occurred.emit(f"Initialization failed: {e}")
            return False
    
    def create_new_gem_configuration(self, name: str, instructions: str = "") -> bool:
        """Create a new gem configuration."""
        try:
            gem_config = GemConfiguration(
                name=name,
                instructions=instructions,
                knowledge_sources=[]
            )
            
            self.current_gem_config = gem_config
            self.knowledge_sources.clear()
            
            logger.info(f"Created new gem configuration: {name}")
            self.status_updated.emit(f"Created new configuration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create gem configuration: {e}")
            self.error_occurred.emit(f"Failed to create configuration: {e}")
            return False
    
    def load_gem_configuration(self, name: str) -> bool:
        """Load a gem configuration."""
        try:
            gem_config = self.config_service.load_gem_configuration(name)
            if not gem_config:
                self.error_occurred.emit(f"Configuration '{name}' not found")
                return False
            
            self.current_gem_config = gem_config
            
            # Load knowledge sources
            self.knowledge_sources.clear()
            for source_path in gem_config.knowledge_sources:
                # TODO: Reconstruct KnowledgeSource objects from paths
                pass
            
            # Update settings
            self.config_service.settings.last_gem_config = name
            self.config_service.save_settings()
            
            logger.info(f"Loaded gem configuration: {name}")
            self.status_updated.emit(f"Loaded configuration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load gem configuration: {e}")
            self.error_occurred.emit(f"Failed to load configuration: {e}")
            return False
    
    def save_gem_configuration(self) -> bool:
        """Save the current gem configuration."""
        try:
            if not self.current_gem_config:
                self.error_occurred.emit("No configuration to save")
                return False
            
            # Update knowledge sources list
            self.current_gem_config.knowledge_sources = [
                source.path for source in self.knowledge_sources
            ]
            
            if self.config_service.save_gem_configuration(self.current_gem_config):
                logger.info(f"Saved gem configuration: {self.current_gem_config.name}")
                self.status_updated.emit("Configuration saved")
                return True
            else:
                self.error_occurred.emit("Failed to save configuration")
                return False
                
        except Exception as e:
            logger.error(f"Failed to save gem configuration: {e}")
            self.error_occurred.emit(f"Failed to save configuration: {e}")
            return False
    
    def update_agent_instructions(self, instructions: str):
        """Update the agent instructions."""
        if self.current_gem_config:
            self.current_gem_config.instructions = instructions
            logger.debug("Agent instructions updated")
    
    def add_knowledge_source(self, path: str, source_type: SourceType) -> Optional[str]:
        """Add a knowledge source."""
        try:
            # Create knowledge source
            source = KnowledgeSource(
                id=f"source_{len(self.knowledge_sources)}_{hash(path)}",
                path=path,
                source_type=source_type,
                name=""
            )
            
            self.knowledge_sources.append(source)
            
            # Process the source in a separate thread
            self._process_knowledge_source_async(source)

            # Start monitoring if it's a file or folder
            if source_type in [SourceType.FILE, SourceType.FOLDER]:
                if self.monitoring_service.add_source_monitoring(source):
                    self.monitoring_status_changed.emit(source.id, True)
                    logger.info(f"Started monitoring: {source.get_display_name()}")

            logger.info(f"Added knowledge source: {source.get_display_name()}")
            return source.id
            
        except Exception as e:
            logger.error(f"Failed to add knowledge source: {e}")
            self.error_occurred.emit(f"Failed to add knowledge source: {e}")
            return None
    
    def _process_knowledge_source_async(self, source: KnowledgeSource):
        """Process knowledge source asynchronously."""
        # TODO: Implement proper async processing with QThread
        try:
            success = self.rag_service.process_knowledge_source(source)
            if success:
                self.knowledge_source_processed.emit(source.id)
            else:
                self.error_occurred.emit(f"Failed to process: {source.get_display_name()}")
        except Exception as e:
            logger.error(f"Error processing knowledge source: {e}")
            self.error_occurred.emit(f"Processing error: {e}")
    
    def remove_knowledge_source(self, source_id: str) -> bool:
        """Remove a knowledge source."""
        try:
            # Find and remove from list
            source_to_remove = None
            for source in self.knowledge_sources:
                if source.id == source_id:
                    source_to_remove = source
                    break
            
            if source_to_remove:
                self.knowledge_sources.remove(source_to_remove)

                # Stop monitoring
                if self.monitoring_service.remove_source_monitoring(source_id):
                    self.monitoring_status_changed.emit(source_id, False)

                # Remove from RAG service
                self.rag_service.remove_source(source_id)

                logger.info(f"Removed knowledge source: {source_to_remove.get_display_name()}")
                return True
            else:
                logger.warning(f"Knowledge source not found: {source_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove knowledge source: {e}")
            self.error_occurred.emit(f"Failed to remove knowledge source: {e}")
            return False
    
    async def send_message(self, message: str, chat_history: List[Dict[str, str]]) -> Optional[str]:
        """Send a message and get AI response."""
        try:
            self.status_updated.emit("Generating response...")
            
            # Get relevant context from RAG
            context = None
            if self.knowledge_sources:
                similar_chunks = self.rag_service.search_similar(message, n_results=3)
                if similar_chunks:
                    context = "\n\n".join([chunk["content"] for chunk in similar_chunks])
            
            # Build full prompt with instructions
            full_prompt = message
            if self.current_gem_config and self.current_gem_config.instructions:
                full_prompt = f"Instructions: {self.current_gem_config.instructions}\n\nUser: {message}"
            
            # Generate response
            response = await self.api_service.generate_response(
                full_prompt, 
                context=context, 
                chat_history=chat_history
            )
            
            if response:
                self.message_received.emit(response)
                self.status_updated.emit("Ready")
                return response
            else:
                self.error_occurred.emit("No response generated")
                self.status_updated.emit("Ready")
                return None
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.error_occurred.emit(f"Failed to send message: {e}")
            self.status_updated.emit("Ready")
            return None
    
    def auto_save(self):
        """Auto-save current configuration."""
        if self.current_gem_config:
            self.save_gem_configuration()
    
    def get_available_configurations(self) -> List[str]:
        """Get list of available gem configurations."""
        return self.config_service.list_gem_configurations()
    
    def get_current_configuration(self) -> Optional[GemConfiguration]:
        """Get the current gem configuration."""
        return self.current_gem_config
    
    def get_knowledge_sources(self) -> List[KnowledgeSource]:
        """Get the current knowledge sources."""
        return self.knowledge_sources.copy()
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return self.rag_service.get_collection_stats()

    def on_file_changed(self, source_id: str, file_path: str, event_type: str):
        """Handle file change events from monitoring service."""
        try:
            logger.info(f"File {event_type}: {file_path} (source: {source_id})")

            # Find the source
            source = None
            for s in self.knowledge_sources:
                if s.id == source_id:
                    source = s
                    break

            if not source:
                logger.warning(f"Source not found for file change: {source_id}")
                return

            if event_type in ["created", "modified"]:
                # Reprocess the source
                self.status_updated.emit(f"Updating knowledge source: {source.get_display_name()}")
                success = self.rag_service.update_source(source)

                if success:
                    self.knowledge_source_updated.emit(source_id, event_type)
                    self.status_updated.emit("Knowledge source updated")
                    logger.info(f"Successfully updated source: {source.get_display_name()}")
                else:
                    self.error_occurred.emit(f"Failed to update source: {source.get_display_name()}")

            elif event_type == "deleted":
                # Handle file deletion
                self.status_updated.emit(f"File deleted from: {source.get_display_name()}")
                # Could implement partial removal logic here

        except Exception as e:
            logger.error(f"Error handling file change: {e}")
            self.error_occurred.emit(f"Error processing file change: {e}")

    def on_monitoring_error(self, source_id: str, error_message: str):
        """Handle monitoring errors."""
        logger.error(f"Monitoring error for {source_id}: {error_message}")
        self.error_occurred.emit(f"Monitoring error: {error_message}")

    def toggle_source_monitoring(self, source_id: str) -> bool:
        """Toggle monitoring for a specific source."""
        try:
            if self.monitoring_service.is_source_monitored(source_id):
                success = self.monitoring_service.remove_source_monitoring(source_id)
                self.monitoring_status_changed.emit(source_id, False)
                return success
            else:
                # Find the source
                source = None
                for s in self.knowledge_sources:
                    if s.id == source_id:
                        source = s
                        break

                if source:
                    success = self.monitoring_service.add_source_monitoring(source)
                    self.monitoring_status_changed.emit(source_id, success)
                    return success

            return False

        except Exception as e:
            logger.error(f"Failed to toggle monitoring for {source_id}: {e}")
            return False

    def reindex_all_sources(self) -> bool:
        """Reindex all knowledge sources."""
        try:
            self.status_updated.emit("Reindexing all knowledge sources...")

            results = self.rag_service.reindex_all_sources(self.knowledge_sources)

            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            if success_count == total_count:
                self.status_updated.emit("All sources reindexed successfully")
                return True
            else:
                self.status_updated.emit(f"Reindexed {success_count}/{total_count} sources")
                return False

        except Exception as e:
            logger.error(f"Failed to reindex sources: {e}")
            self.error_occurred.emit(f"Failed to reindex sources: {e}")
            return False

    def get_monitoring_status(self) -> Dict[str, Dict]:
        """Get monitoring status for all sources."""
        return self.monitoring_service.get_monitored_sources()

    def add_url_source(self, url: str, config: Dict[str, Any]) -> Optional[str]:
        """Add a URL/website as a knowledge source."""
        try:
            # Create knowledge source
            source = KnowledgeSource(
                id=f"url_{len(self.knowledge_sources)}_{hash(url)}",
                path=url,
                source_type=SourceType.URL,
                name="",
                config=config
            )

            self.knowledge_sources.append(source)

            # Process the source
            self._process_knowledge_source_async(source)

            logger.info(f"Added URL source: {url}")
            return source.id

        except Exception as e:
            logger.error(f"Failed to add URL source: {e}")
            self.error_occurred.emit(f"Failed to add URL source: {e}")
            return None

    def add_google_drive_source(self, folder_url: str) -> Optional[str]:
        """Add a Google Drive folder as a knowledge source."""
        try:
            # Check if Google Drive is authenticated
            if not self.rag_service.google_drive_service.is_authenticated():
                self.google_drive_auth_needed.emit()
                return None

            # Create knowledge source
            source = KnowledgeSource(
                id=f"gdrive_{len(self.knowledge_sources)}_{hash(folder_url)}",
                path=folder_url,
                source_type=SourceType.GOOGLE_DRIVE,
                name=""
            )

            self.knowledge_sources.append(source)

            # Process the source
            self._process_knowledge_source_async(source)

            logger.info(f"Added Google Drive source: {folder_url}")
            return source.id

        except Exception as e:
            logger.error(f"Failed to add Google Drive source: {e}")
            self.error_occurred.emit(f"Failed to add Google Drive source: {e}")
            return None

    def authenticate_google_drive(self, credentials_file: Optional[str] = None) -> bool:
        """Authenticate with Google Drive."""
        try:
            success = self.rag_service.google_drive_service.authenticate(credentials_file)
            if success:
                self.status_updated.emit("Google Drive authenticated successfully")
            else:
                self.error_occurred.emit("Google Drive authentication failed")
            return success

        except Exception as e:
            logger.error(f"Google Drive authentication error: {e}")
            self.error_occurred.emit(f"Google Drive authentication error: {e}")
            return False

    def start_batch_processing(self, source_infos: List[Dict[str, Any]]) -> bool:
        """Start batch processing of multiple sources."""
        try:
            # Convert source infos to KnowledgeSource objects
            sources = []
            for info in source_infos:
                source = KnowledgeSource(
                    id=info.get("id", f"batch_{len(sources)}"),
                    path=info.get("path", ""),
                    source_type=SourceType(info.get("type", "file")),
                    name=info.get("name", ""),
                    config=info.get("config", {})
                )
                sources.append(source)

            # Start batch processing
            success = self.batch_processing_service.process_sources_batch(sources)

            if success:
                self.status_updated.emit(f"Started batch processing of {len(sources)} sources")
            else:
                self.error_occurred.emit("Failed to start batch processing")

            return success

        except Exception as e:
            logger.error(f"Failed to start batch processing: {e}")
            self.error_occurred.emit(f"Failed to start batch processing: {e}")
            return False

    def stop_batch_processing(self):
        """Stop current batch processing."""
        try:
            self.batch_processing_service.stop_batch_processing()
            self.status_updated.emit("Batch processing stopped")

        except Exception as e:
            logger.error(f"Failed to stop batch processing: {e}")
            self.error_occurred.emit(f"Failed to stop batch processing: {e}")

    def get_batch_processing_status(self) -> Dict[str, Any]:
        """Get current batch processing status."""
        return self.batch_processing_service.get_processing_statistics()

    def is_batch_processing(self) -> bool:
        """Check if batch processing is currently running."""
        return self.batch_processing_service.is_processing()

    # Epic 5: Configuration & Session Management Methods

    def create_enhanced_configuration(self, name: str, instructions: str = "",
                                    description: str = "", category: str = "general") -> Optional[str]:
        """Create a new enhanced configuration."""
        try:
            config = EnhancedGemConfiguration(
                name=name,
                instructions=instructions,
                description=description,
                category=category
            )

            # Save configuration
            if self.workspace_service.save_configuration(config):
                # Add to current workspace
                self.workspace_service.add_configuration_to_workspace(
                    self.current_workspace_id, config.id
                )

                # Update session
                self.session_service.set_current_configuration(config.id)

                self.current_gem_config = config
                self.knowledge_sources.clear()

                logger.info(f"Created enhanced configuration: {name}")
                self.status_updated.emit(f"Created configuration: {name}")
                self.configuration_created.emit(config.id)
                return config.id
            else:
                self.error_occurred.emit("Failed to save configuration")
                return None

        except Exception as e:
            logger.error(f"Failed to create enhanced configuration: {e}")
            self.error_occurred.emit(f"Failed to create configuration: {e}")
            return None

    def load_enhanced_configuration(self, config_id: str) -> bool:
        """Load an enhanced configuration."""
        try:
            config = self.workspace_service.load_configuration(config_id)
            if not config:
                self.error_occurred.emit(f"Configuration '{config_id}' not found")
                return False

            self.current_gem_config = config

            # Update usage statistics
            config.update_usage()
            self.workspace_service.save_configuration(config)

            # Update session
            self.session_service.set_current_configuration(config_id)

            # Load knowledge sources
            self.knowledge_sources.clear()
            for source_data in config.knowledge_sources:
                # Reconstruct KnowledgeSource objects
                try:
                    source = KnowledgeSource(
                        id=source_data.get("id", ""),
                        path=source_data.get("path", ""),
                        source_type=SourceType(source_data.get("type", "file")),
                        name=source_data.get("name", ""),
                        config=source_data.get("config", {})
                    )
                    self.knowledge_sources.append(source)
                except Exception as e:
                    logger.error(f"Failed to reconstruct knowledge source: {e}")
                    continue

            logger.info(f"Loaded enhanced configuration: {config.name}")
            self.status_updated.emit(f"Loaded configuration: {config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load enhanced configuration: {e}")
            self.error_occurred.emit(f"Failed to load configuration: {e}")
            return False

    def save_enhanced_configuration(self) -> bool:
        """Save the current enhanced configuration."""
        try:
            if not self.current_gem_config:
                self.error_occurred.emit("No configuration to save")
                return False

            # Update knowledge sources list
            self.current_gem_config.knowledge_sources = [
                {
                    "id": source.id,
                    "path": source.path,
                    "type": source.source_type.value,
                    "name": source.name,
                    "config": source.config
                }
                for source in self.knowledge_sources
            ]

            if self.workspace_service.save_configuration(self.current_gem_config):
                logger.info(f"Saved enhanced configuration: {self.current_gem_config.name}")
                self.status_updated.emit("Configuration saved")
                return True
            else:
                self.error_occurred.emit("Failed to save configuration")
                return False

        except Exception as e:
            logger.error(f"Failed to save enhanced configuration: {e}")
            self.error_occurred.emit(f"Failed to save configuration: {e}")
            return False

    def duplicate_configuration(self, config_id: str, new_name: str) -> Optional[str]:
        """Duplicate a configuration."""
        try:
            new_config = self.workspace_service.duplicate_configuration(config_id, new_name)
            if new_config:
                # Add to current workspace
                self.workspace_service.add_configuration_to_workspace(
                    self.current_workspace_id, new_config.id
                )

                logger.info(f"Duplicated configuration: {new_name}")
                self.status_updated.emit(f"Duplicated configuration: {new_name}")
                self.configuration_created.emit(new_config.id)
                return new_config.id
            else:
                self.error_occurred.emit("Failed to duplicate configuration")
                return None

        except Exception as e:
            logger.error(f"Failed to duplicate configuration: {e}")
            self.error_occurred.emit(f"Failed to duplicate configuration: {e}")
            return None

    def delete_configuration(self, config_id: str) -> bool:
        """Delete a configuration."""
        try:
            # Remove from all workspaces
            workspaces = self.workspace_service.list_workspaces()
            for workspace in workspaces:
                if config_id in workspace.configurations:
                    self.workspace_service.remove_configuration_from_workspace(
                        workspace.id, config_id
                    )

            # Delete configuration file
            config_file = self.workspace_service.configurations_dir / f"{config_id}.json"
            if config_file.exists():
                config_file.unlink()

                logger.info(f"Deleted configuration: {config_id}")
                self.status_updated.emit("Configuration deleted")
                return True
            else:
                self.error_occurred.emit("Configuration file not found")
                return False

        except Exception as e:
            logger.error(f"Failed to delete configuration: {e}")
            self.error_occurred.emit(f"Failed to delete configuration: {e}")
            return False

    # Workspace Management Methods

    def create_workspace(self, name: str, description: str = "",
                        workspace_type: str = "personal") -> Optional[str]:
        """Create a new workspace."""
        try:
            from models.workspace import WorkspaceType

            workspace = self.workspace_service.create_workspace(
                name=name,
                description=description,
                workspace_type=WorkspaceType(workspace_type)
            )

            if workspace:
                logger.info(f"Created workspace: {name}")
                self.status_updated.emit(f"Created workspace: {name}")
                return workspace.id
            else:
                self.error_occurred.emit("Failed to create workspace")
                return None

        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            self.error_occurred.emit(f"Failed to create workspace: {e}")
            return None

    def switch_workspace(self, workspace_id: str) -> bool:
        """Switch to a different workspace."""
        try:
            workspace = self.workspace_service.load_workspace(workspace_id)
            if not workspace:
                self.error_occurred.emit(f"Workspace '{workspace_id}' not found")
                return False

            self.current_workspace_id = workspace_id
            self.session_service.set_current_workspace(workspace_id)

            logger.info(f"Switched to workspace: {workspace.name}")
            self.status_updated.emit(f"Switched to workspace: {workspace.name}")
            self.workspace_changed.emit(workspace_id)
            return True

        except Exception as e:
            logger.error(f"Failed to switch workspace: {e}")
            self.error_occurred.emit(f"Failed to switch workspace: {e}")
            return False

    def get_workspace_configurations(self, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get configurations for a workspace."""
        try:
            if workspace_id is None:
                workspace_id = self.current_workspace_id

            configurations = self.workspace_service.list_configurations(workspace_id)
            return [config.model_dump() for config in configurations]

        except Exception as e:
            logger.error(f"Failed to get workspace configurations: {e}")
            return []

    def get_all_workspaces(self) -> List[Dict[str, Any]]:
        """Get all available workspaces."""
        try:
            workspaces = self.workspace_service.list_workspaces()
            return [workspace.model_dump() for workspace in workspaces]

        except Exception as e:
            logger.error(f"Failed to get workspaces: {e}")
            return []

    # Template Management Methods

    def apply_template(self, template_name: str, config_name: str) -> Optional[str]:
        """Apply a template to create a new configuration."""
        try:
            config_data = self.template_service.apply_template(template_name, config_name)
            if not config_data:
                self.error_occurred.emit(f"Failed to apply template: {template_name}")
                return None

            # Create enhanced configuration from template
            config = EnhancedGemConfiguration(**config_data)

            if self.workspace_service.save_configuration(config):
                # Add to current workspace
                self.workspace_service.add_configuration_to_workspace(
                    self.current_workspace_id, config.id
                )

                logger.info(f"Applied template '{template_name}' to create '{config_name}'")
                self.status_updated.emit(f"Created configuration from template: {config_name}")
                self.template_applied.emit(template_name, config_name)
                self.configuration_created.emit(config.id)
                return config.id
            else:
                self.error_occurred.emit("Failed to save configuration from template")
                return None

        except Exception as e:
            logger.error(f"Failed to apply template: {e}")
            self.error_occurred.emit(f"Failed to apply template: {e}")
            return None

    def create_template_from_configuration(self, config_id: str, template_name: str,
                                         description: str = "", category: str = "custom") -> bool:
        """Create a template from an existing configuration."""
        try:
            config = self.workspace_service.load_configuration(config_id)
            if not config:
                self.error_occurred.emit(f"Configuration '{config_id}' not found")
                return False

            template = self.template_service.create_template_from_configuration(
                config, template_name, description, category
            )

            if template:
                logger.info(f"Created template '{template_name}' from configuration")
                self.status_updated.emit(f"Created template: {template_name}")
                return True
            else:
                self.error_occurred.emit("Failed to create template")
                return False

        except Exception as e:
            logger.error(f"Failed to create template from configuration: {e}")
            self.error_occurred.emit(f"Failed to create template: {e}")
            return False

    def get_all_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all available templates."""
        try:
            templates = self.template_service.list_templates(category)
            return [template.model_dump() for template in templates]

        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []

    def get_template_categories(self) -> List[str]:
        """Get all template categories."""
        try:
            return self.template_service.get_categories()
        except Exception as e:
            logger.error(f"Failed to get template categories: {e}")
            return []

    # Import/Export Methods

    def export_configuration(self, config_id: str, include_knowledge_sources: bool = True) -> Optional[str]:
        """Export a configuration to file."""
        try:
            export_path = self.import_export_service.export_configuration(
                config_id, include_knowledge_sources
            )

            if export_path:
                logger.info(f"Exported configuration to: {export_path}")
                self.status_updated.emit(f"Configuration exported to: {export_path}")
                self.export_completed.emit(export_path)
                return export_path
            else:
                self.error_occurred.emit("Failed to export configuration")
                return None

        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            self.error_occurred.emit(f"Failed to export configuration: {e}")
            return None

    def export_workspace(self, workspace_id: str, include_configurations: bool = True,
                        include_knowledge_sources: bool = True) -> Optional[str]:
        """Export a workspace to file."""
        try:
            export_path = self.import_export_service.export_workspace(
                workspace_id, include_configurations, include_knowledge_sources
            )

            if export_path:
                logger.info(f"Exported workspace to: {export_path}")
                self.status_updated.emit(f"Workspace exported to: {export_path}")
                self.export_completed.emit(export_path)
                return export_path
            else:
                self.error_occurred.emit("Failed to export workspace")
                return None

        except Exception as e:
            logger.error(f"Failed to export workspace: {e}")
            self.error_occurred.emit(f"Failed to export workspace: {e}")
            return None

    def create_backup(self, include_knowledge_sources: bool = False) -> Optional[str]:
        """Create a complete backup."""
        try:
            backup_path = self.import_export_service.create_backup(include_knowledge_sources)

            if backup_path:
                logger.info(f"Created backup at: {backup_path}")
                self.status_updated.emit(f"Backup created: {backup_path}")
                self.export_completed.emit(backup_path)
                return backup_path
            else:
                self.error_occurred.emit("Failed to create backup")
                return None

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            self.error_occurred.emit(f"Failed to create backup: {e}")
            return None

    def import_from_file(self, file_path: str, merge_mode: str = "skip") -> Dict[str, Any]:
        """Import data from file."""
        try:
            results = self.import_export_service.import_from_file(file_path, merge_mode)

            if "error" not in results:
                logger.info(f"Import completed: {results}")
                self.status_updated.emit("Import completed successfully")
                self.import_completed.emit(results)
            else:
                self.error_occurred.emit(f"Import failed: {results['error']}")

            return results

        except Exception as e:
            logger.error(f"Failed to import from file: {e}")
            self.error_occurred.emit(f"Failed to import: {e}")
            return {"error": str(e)}

    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get export file history."""
        try:
            return self.import_export_service.get_export_history()
        except Exception as e:
            logger.error(f"Failed to get export history: {e}")
            return []

    # Session Management Methods

    def save_window_state(self, geometry: Dict[str, int]):
        """Save window geometry to session."""
        try:
            self.session_service.save_window_geometry(geometry)
        except Exception as e:
            logger.error(f"Failed to save window state: {e}")

    def get_window_state(self) -> Dict[str, int]:
        """Get saved window geometry."""
        try:
            return self.session_service.get_window_geometry()
        except Exception as e:
            logger.error(f"Failed to get window state: {e}")
            return {"x": 100, "y": 100, "width": 1200, "height": 800}

    def save_panel_state(self, panel_name: str, is_visible: bool):
        """Save panel visibility state."""
        try:
            self.session_service.save_panel_state(panel_name, is_visible)
        except Exception as e:
            logger.error(f"Failed to save panel state: {e}")

    def get_panel_state(self, panel_name: str, default: bool = True) -> bool:
        """Get panel visibility state."""
        try:
            return self.session_service.get_panel_state(panel_name, default)
        except Exception as e:
            logger.error(f"Failed to get panel state: {e}")
            return default

    def get_recent_configurations(self) -> List[str]:
        """Get recent configuration IDs."""
        try:
            return self.session_service.get_recent_configurations()
        except Exception as e:
            logger.error(f"Failed to get recent configurations: {e}")
            return []

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            return self.session_service.get_session_statistics()
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {}

    def search_configurations(self, query: str, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search configurations."""
        try:
            if workspace_id is None:
                workspace_id = self.current_workspace_id

            configurations = self.workspace_service.search_configurations(query, workspace_id)
            return [config.model_dump() for config in configurations]

        except Exception as e:
            logger.error(f"Failed to search configurations: {e}")
            return []

    def get_workspace_statistics(self, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workspace statistics."""
        try:
            if workspace_id is None:
                workspace_id = self.current_workspace_id

            return self.workspace_service.get_workspace_statistics(workspace_id)

        except Exception as e:
            logger.error(f"Failed to get workspace statistics: {e}")
            return {}
