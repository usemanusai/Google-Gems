"""
Main Window for Custom Gemini Agent GUI

This module contains the MainWindow class which serves as the primary
user interface for the application.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QListWidget, QPushButton,
    QLabel, QLineEdit, QGroupBox, QMenuBar, QStatusBar,
    QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from loguru import logger
from pathlib import Path

from services.config_service import ConfigService
from controllers.main_controller import MainController
from workers.message_worker import MessageWorker
from widgets.instructions_widget import InstructionsWidget
from widgets.knowledge_widget import KnowledgeWidget
from widgets.chat_widget import ChatWidget
from widgets.configuration_manager_widget import ConfigurationManagerWidget
from widgets.settings_widget import SettingsWidget
from models.knowledge_source import SourceType


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config_service: ConfigService):
        super().__init__()
        self.config_service = config_service
        self.settings_widget = None

        # Initialize controller
        self.controller = MainController()

        # Initialize message worker
        self.message_worker = MessageWorker(self.controller)

        self.init_ui()
        self.connect_signals()
        self.load_session_state()

        # Initialize controller after UI is ready
        self.controller.initialize()

        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Custom Gemini Agent GUI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Create left panel (Instructions and Knowledge)
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Create right panel (Chat/Preview)
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 800])
        
        logger.debug("UI initialized")

    def connect_signals(self):
        """Connect signals between widgets and controller."""
        # Chat widget signals
        self.chat_widget.message_sent.connect(self.on_message_sent)

        # Connect stop button to worker
        self.chat_widget.stop_button.clicked.connect(self.message_worker.stop_processing)

        # Controller signals
        self.controller.status_updated.connect(self.status_bar.showMessage)
        self.controller.knowledge_source_processed.connect(self.on_knowledge_source_processed)
        self.controller.knowledge_source_updated.connect(self.on_knowledge_source_updated)
        self.controller.monitoring_status_changed.connect(self.on_monitoring_status_changed)
        self.controller.batch_processing_started.connect(self.on_batch_processing_started)
        self.controller.batch_processing_completed.connect(self.on_batch_processing_completed)
        self.controller.google_drive_auth_needed.connect(self.on_google_drive_auth_needed)

        # Epic 5 signals
        self.controller.workspace_changed.connect(self.on_workspace_changed)
        self.controller.configuration_created.connect(self.on_configuration_created)
        self.controller.template_applied.connect(self.on_template_applied)
        self.controller.import_completed.connect(self.on_import_completed)
        self.controller.export_completed.connect(self.on_export_completed)

        # Message worker signals
        self.message_worker.response_received.connect(self.chat_widget.add_assistant_message)
        self.message_worker.error_occurred.connect(self.chat_widget.add_error_message)
        self.message_worker.status_updated.connect(self.status_bar.showMessage)

        # Instructions widget signals
        self.instructions_widget.instructions_changed.connect(self.controller.update_agent_instructions)
        self.instructions_widget.agent_name_changed.connect(self.on_agent_name_changed)

        # Knowledge widget signals
        self.knowledge_widget.knowledge_sources_changed.connect(self.on_knowledge_sources_changed)
        self.knowledge_widget.monitoring_toggle_requested.connect(self.controller.toggle_source_monitoring)
        self.knowledge_widget.reindex_requested.connect(self.controller.reindex_all_sources)
        self.knowledge_widget.batch_process_requested.connect(self.controller.start_batch_processing)
        self.knowledge_widget.google_drive_auth_requested.connect(self.on_google_drive_auth_requested)
        self.knowledge_widget.url_source_requested.connect(self.controller.add_url_source)

        logger.debug("Signals connected")
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_gem_action = QAction('&New Gem Configuration', self)
        new_gem_action.setShortcut('Ctrl+N')
        new_gem_action.triggered.connect(self.new_gem_configuration)
        file_menu.addAction(new_gem_action)
        
        load_gem_action = QAction('&Load Gem Configuration', self)
        load_gem_action.setShortcut('Ctrl+O')
        load_gem_action.triggered.connect(self.load_gem_configuration)
        file_menu.addAction(load_gem_action)
        
        save_gem_action = QAction('&Save Gem Configuration', self)
        save_gem_action.setShortcut('Ctrl+S')
        save_gem_action.triggered.connect(self.save_gem_configuration)
        file_menu.addAction(save_gem_action)
        
        file_menu.addSeparator()

        # Import/Export submenu
        import_export_menu = file_menu.addMenu('Import/Export')

        export_config_action = QAction('Export Configuration', self)
        export_config_action.triggered.connect(self.export_configuration)
        import_export_menu.addAction(export_config_action)

        export_workspace_action = QAction('Export Workspace', self)
        export_workspace_action.triggered.connect(self.export_workspace)
        import_export_menu.addAction(export_workspace_action)

        import_export_menu.addSeparator()

        import_action = QAction('Import from File', self)
        import_action.triggered.connect(self.import_from_file)
        import_export_menu.addAction(import_action)

        backup_action = QAction('Create Backup', self)
        backup_action.triggered.connect(self.create_backup)
        import_export_menu.addAction(backup_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Workspace menu
        workspace_menu = menubar.addMenu('&Workspace')

        new_workspace_action = QAction('New Workspace', self)
        new_workspace_action.triggered.connect(self.new_workspace)
        workspace_menu.addAction(new_workspace_action)

        switch_workspace_action = QAction('Switch Workspace', self)
        switch_workspace_action.triggered.connect(self.switch_workspace)
        workspace_menu.addAction(switch_workspace_action)

        workspace_menu.addSeparator()

        manage_configs_action = QAction('Manage Configurations', self)
        manage_configs_action.triggered.connect(self.show_configuration_manager)
        workspace_menu.addAction(manage_configs_action)

        # Templates menu
        templates_menu = menubar.addMenu('&Templates')

        apply_template_action = QAction('Apply Template', self)
        apply_template_action.triggered.connect(self.apply_template)
        templates_menu.addAction(apply_template_action)

        create_template_action = QAction('Create Template from Current', self)
        create_template_action.triggered.connect(self.create_template)
        templates_menu.addAction(create_template_action)

        # Settings menu
        settings_menu = menubar.addMenu('&Settings')
        
        api_settings_action = QAction('&API Settings', self)
        api_settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(api_settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_left_panel(self):
        """Create the left panel with instructions and knowledge widgets."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create vertical splitter for left panel
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_layout.addWidget(left_splitter)
        
        # Instructions widget
        self.instructions_widget = InstructionsWidget()
        left_splitter.addWidget(self.instructions_widget)
        
        # Knowledge widget
        self.knowledge_widget = KnowledgeWidget()
        left_splitter.addWidget(self.knowledge_widget)
        
        # Set splitter proportions
        left_splitter.setSizes([300, 500])
        
        return left_widget
    
    def create_right_panel(self):
        """Create the right panel with chat/preview widget."""
        # Chat widget
        self.chat_widget = ChatWidget()

        # Configuration manager widget (initially hidden)
        self.config_manager_widget = ConfigurationManagerWidget()
        self.config_manager_widget.setVisible(False)

        return self.chat_widget
    
    def on_message_sent(self, message: str):
        """Handle message sent from chat widget."""
        # Get chat history
        chat_history = self.chat_widget.get_chat_history()

        # Send message through worker thread
        self.message_worker.send_message(message, chat_history)

    def on_knowledge_source_processed(self, source_id: str):
        """Handle knowledge source processing completion."""
        self.status_bar.showMessage(f"Knowledge source processed: {source_id}")
        self.knowledge_widget.update_source_status(source_id, "indexed")
        logger.info(f"Knowledge source processed: {source_id}")

    def on_knowledge_source_updated(self, source_id: str, event_type: str):
        """Handle knowledge source updates from file monitoring."""
        self.status_bar.showMessage(f"Knowledge source updated: {source_id} ({event_type})")
        self.knowledge_widget.update_source_status(source_id, "indexed")
        logger.info(f"Knowledge source updated: {source_id} ({event_type})")

    def on_monitoring_status_changed(self, source_id: str, is_monitoring: bool):
        """Handle monitoring status changes."""
        status = "monitoring" if is_monitoring else "indexed"
        self.knowledge_widget.update_source_status(source_id, status, is_monitoring)
        action = "started" if is_monitoring else "stopped"
        self.status_bar.showMessage(f"Monitoring {action} for source: {source_id}")
        logger.info(f"Monitoring {action} for source: {source_id}")

    def on_batch_processing_started(self, total_jobs: int):
        """Handle batch processing started."""
        self.status_bar.showMessage(f"Batch processing started: {total_jobs} jobs")
        QMessageBox.information(
            self,
            "Batch Processing",
            f"Started batch processing of {total_jobs} sources.\n\n"
            "This may take some time. You can continue using the application."
        )
        logger.info(f"Batch processing started with {total_jobs} jobs")

    def on_batch_processing_completed(self, successful: int, total: int):
        """Handle batch processing completed."""
        self.status_bar.showMessage(f"Batch processing completed: {successful}/{total} successful")

        if successful == total:
            QMessageBox.information(
                self,
                "Batch Processing Complete",
                f"Successfully processed all {total} sources!"
            )
        else:
            QMessageBox.warning(
                self,
                "Batch Processing Complete",
                f"Processed {successful} out of {total} sources.\n\n"
                f"{total - successful} sources failed to process."
            )

        logger.info(f"Batch processing completed: {successful}/{total} successful")

    def on_google_drive_auth_requested(self):
        """Handle Google Drive authentication request."""
        self.authenticate_google_drive()

    def on_google_drive_auth_needed(self):
        """Handle Google Drive authentication needed signal."""
        reply = QMessageBox.question(
            self,
            "Google Drive Authentication",
            "Google Drive access requires authentication.\n\n"
            "Would you like to authenticate now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.authenticate_google_drive()

    def authenticate_google_drive(self):
        """Authenticate with Google Drive."""
        # Ask for credentials file
        credentials_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Google Drive Credentials File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if credentials_file:
            success = self.controller.authenticate_google_drive(credentials_file)
            if success:
                QMessageBox.information(
                    self,
                    "Google Drive Authentication",
                    "Google Drive authenticated successfully!\n\n"
                    "You can now add Google Drive folders to your knowledge base."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Google Drive Authentication",
                    "Google Drive authentication failed.\n\n"
                    "Please check your credentials file and try again."
                )

    # Epic 5: Configuration & Session Management Methods

    def show_configuration_manager(self):
        """Show the configuration manager widget."""
        if hasattr(self, 'config_manager_widget'):
            # Create a dialog to show the configuration manager
            from PyQt6.QtWidgets import QDialog, QVBoxLayout

            dialog = QDialog(self)
            dialog.setWindowTitle("Configuration Manager")
            dialog.setModal(False)
            dialog.resize(1000, 700)

            layout = QVBoxLayout(dialog)
            layout.addWidget(self.config_manager_widget)

            # Update data
            self.update_configuration_manager_data()

            dialog.show()

    def update_configuration_manager_data(self):
        """Update configuration manager with current data."""
        if hasattr(self, 'config_manager_widget'):
            # Get data from controller
            configurations = self.controller.get_workspace_configurations()
            workspaces = self.controller.get_all_workspaces()
            templates = self.controller.get_all_templates()

            # Update widget
            self.config_manager_widget.update_configurations(configurations)
            self.config_manager_widget.update_workspaces(workspaces)
            self.config_manager_widget.update_templates(templates)

    def new_workspace(self):
        """Create a new workspace."""
        name, ok = QInputDialog.getText(
            self,
            "New Workspace",
            "Enter workspace name:",
            text="My Workspace"
        )

        if ok and name.strip():
            workspace_id = self.controller.create_workspace(name.strip())
            if workspace_id:
                QMessageBox.information(
                    self,
                    "Workspace Created",
                    f"Workspace '{name}' created successfully!"
                )

    def switch_workspace(self):
        """Switch to a different workspace."""
        workspaces = self.controller.get_all_workspaces()
        if not workspaces:
            QMessageBox.information(
                self,
                "No Workspaces",
                "No workspaces available."
            )
            return

        workspace_names = [ws["name"] for ws in workspaces]

        name, ok = QInputDialog.getItem(
            self,
            "Switch Workspace",
            "Select workspace:",
            workspace_names,
            0,
            False
        )

        if ok and name:
            # Find workspace ID by name
            for workspace in workspaces:
                if workspace["name"] == name:
                    if self.controller.switch_workspace(workspace["id"]):
                        QMessageBox.information(
                            self,
                            "Workspace Switched",
                            f"Switched to workspace: {name}"
                        )
                    break

    def apply_template(self):
        """Apply a template to create a new configuration."""
        templates = self.controller.get_all_templates()
        if not templates:
            QMessageBox.information(
                self,
                "No Templates",
                "No templates available."
            )
            return

        template_names = [t["name"] for t in templates]

        template_name, ok = QInputDialog.getItem(
            self,
            "Apply Template",
            "Select template:",
            template_names,
            0,
            False
        )

        if ok and template_name:
            config_name, ok = QInputDialog.getText(
                self,
                "Configuration Name",
                "Enter name for new configuration:",
                text=f"Config from {template_name}"
            )

            if ok and config_name.strip():
                config_id = self.controller.apply_template(template_name, config_name.strip())
                if config_id:
                    QMessageBox.information(
                        self,
                        "Template Applied",
                        f"Created configuration '{config_name}' from template '{template_name}'"
                    )

    def create_template(self):
        """Create a template from current configuration."""
        if not self.controller.current_gem_config:
            QMessageBox.warning(
                self,
                "No Configuration",
                "No configuration is currently loaded."
            )
            return

        template_name, ok = QInputDialog.getText(
            self,
            "Create Template",
            "Enter template name:",
            text=f"{self.controller.current_gem_config.name} Template"
        )

        if ok and template_name.strip():
            description, ok = QInputDialog.getText(
                self,
                "Template Description",
                "Enter template description (optional):"
            )

            if ok:
                if self.controller.create_template_from_configuration(
                    self.controller.current_gem_config.id,
                    template_name.strip(),
                    description.strip()
                ):
                    QMessageBox.information(
                        self,
                        "Template Created",
                        f"Template '{template_name}' created successfully!"
                    )

    def export_configuration(self):
        """Export current configuration."""
        if not self.controller.current_gem_config:
            QMessageBox.warning(
                self,
                "No Configuration",
                "No configuration is currently loaded."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            f"{self.controller.current_gem_config.name}.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            export_path = self.controller.export_configuration(
                self.controller.current_gem_config.id
            )
            if export_path:
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Configuration exported to:\n{export_path}"
                )

    def export_workspace(self):
        """Export current workspace."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Workspace",
            "workspace_export.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            export_path = self.controller.export_workspace(
                self.controller.current_workspace_id
            )
            if export_path:
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Workspace exported to:\n{export_path}"
                )

    def import_from_file(self):
        """Import configurations from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import from File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            # Ask about merge mode
            from PyQt6.QtWidgets import QButtonGroup, QRadioButton, QDialog, QVBoxLayout

            dialog = QDialog(self)
            dialog.setWindowTitle("Import Options")
            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel("How to handle conflicts:"))

            skip_radio = QRadioButton("Skip existing items")
            skip_radio.setChecked(True)
            layout.addWidget(skip_radio)

            overwrite_radio = QRadioButton("Overwrite existing items")
            layout.addWidget(overwrite_radio)

            rename_radio = QRadioButton("Rename conflicting items")
            layout.addWidget(rename_radio)

            buttons = QHBoxLayout()
            ok_button = QPushButton("Import")
            cancel_button = QPushButton("Cancel")

            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)

            buttons.addWidget(cancel_button)
            buttons.addWidget(ok_button)
            layout.addLayout(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                merge_mode = "skip"
                if overwrite_radio.isChecked():
                    merge_mode = "overwrite"
                elif rename_radio.isChecked():
                    merge_mode = "rename"

                results = self.controller.import_from_file(file_path, merge_mode)

                if "error" not in results:
                    QMessageBox.information(
                        self,
                        "Import Complete",
                        f"Import completed:\n"
                        f"Configurations: {results['configurations']['imported']} imported, "
                        f"{results['configurations']['skipped']} skipped\n"
                        f"Workspaces: {results['workspaces']['imported']} imported, "
                        f"{results['workspaces']['skipped']} skipped\n"
                        f"Templates: {results['templates']['imported']} imported, "
                        f"{results['templates']['skipped']} skipped"
                    )

    def create_backup(self):
        """Create a complete backup."""
        reply = QMessageBox.question(
            self,
            "Create Backup",
            "Include knowledge source files in backup?\n\n"
            "This will make the backup larger but more complete.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        include_knowledge_sources = reply == QMessageBox.StandardButton.Yes

        backup_path = self.controller.create_backup(include_knowledge_sources)
        if backup_path:
            QMessageBox.information(
                self,
                "Backup Complete",
                f"Backup created at:\n{backup_path}"
            )

    # Epic 5 Signal Handlers

    def on_workspace_changed(self, workspace_id: str):
        """Handle workspace change."""
        self.status_bar.showMessage(f"Switched to workspace: {workspace_id}")
        logger.info(f"Workspace changed to: {workspace_id}")

    def on_configuration_created(self, config_id: str):
        """Handle configuration creation."""
        self.status_bar.showMessage(f"Configuration created: {config_id}")
        logger.info(f"Configuration created: {config_id}")

    def on_template_applied(self, template_name: str, config_name: str):
        """Handle template application."""
        self.status_bar.showMessage(f"Applied template '{template_name}' to create '{config_name}'")
        logger.info(f"Template applied: {template_name} -> {config_name}")

    def on_import_completed(self, results: dict):
        """Handle import completion."""
        total_imported = (results.get('configurations', {}).get('imported', 0) +
                         results.get('workspaces', {}).get('imported', 0) +
                         results.get('templates', {}).get('imported', 0))
        self.status_bar.showMessage(f"Import completed: {total_imported} items imported")
        logger.info(f"Import completed: {results}")

    def on_export_completed(self, export_path: str):
        """Handle export completion."""
        self.status_bar.showMessage(f"Export completed: {export_path}")
        logger.info(f"Export completed: {export_path}")

    def load_session_state(self):
        """Load session state including window geometry."""
        try:
            geometry = self.controller.get_window_state()
            self.setGeometry(
                geometry.get("x", 100),
                geometry.get("y", 100),
                geometry.get("width", 1200),
                geometry.get("height", 800)
            )
            logger.debug("Loaded session state")
        except Exception as e:
            logger.error(f"Failed to load session state: {e}")

    def save_session_state(self):
        """Save session state including window geometry."""
        try:
            geometry = {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height()
            }
            self.controller.save_window_state(geometry)
            logger.debug("Saved session state")
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Save session state
            self.save_session_state()

            # Save current configuration if any
            if self.controller.current_gem_config:
                self.controller.save_enhanced_configuration()

            logger.info("Application closing")
            event.accept()
        except Exception as e:
            logger.error(f"Error during close: {e}")
            event.accept()
        else:
            QMessageBox.information(
                self,
                "Google Drive Setup",
                "To use Google Drive integration:\n\n"
                "1. Go to Google Cloud Console\n"
                "2. Create a project and enable Drive API\n"
                "3. Create credentials (OAuth 2.0)\n"
                "4. Download the credentials JSON file\n"
                "5. Use that file for authentication"
            )

    def on_agent_name_changed(self, name: str):
        """Handle agent name change."""
        if self.controller.current_gem_config:
            self.controller.current_gem_config.name = name
        else:
            # Create new configuration
            self.controller.create_new_gem_configuration(name)

    def on_knowledge_sources_changed(self, sources: list):
        """Handle knowledge sources change."""
        # Add new sources to controller
        for source_info in sources:
            source_type = SourceType(source_info.get("type", "file"))
            source_path = source_info.get("path", "")
            if source_path:
                self.controller.add_knowledge_source(source_path, source_type)

    def new_gem_configuration(self):
        """Create a new gem configuration."""
        from PyQt6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "New Configuration", "Enter configuration name:")
        if ok and name.strip():
            if self.controller.create_new_gem_configuration(name.strip()):
                self.instructions_widget.set_agent_name(name.strip())
                self.instructions_widget.clear_instructions()
                self.knowledge_widget.clear_all_sources()
                self.chat_widget.clear_chat()
                logger.info(f"Created new gem configuration: {name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to create new configuration")
    
    def load_gem_configuration(self):
        """Load a gem configuration from file."""
        from PyQt6.QtWidgets import QInputDialog

        # Get available configurations
        configs = self.controller.get_available_configurations()
        if not configs:
            QMessageBox.information(self, "Load Configuration", "No saved configurations found.")
            return

        # Show selection dialog
        config_name, ok = QInputDialog.getItem(
            self, "Load Configuration", "Select configuration:", configs, 0, False
        )

        if ok and config_name:
            if self.controller.load_gem_configuration(config_name):
                # Update UI with loaded configuration
                config = self.controller.get_current_configuration()
                if config:
                    self.instructions_widget.set_agent_name(config.name)
                    self.instructions_widget.set_instructions(config.instructions)
                    # TODO: Update knowledge widget with sources
                logger.info(f"Loaded gem configuration: {config_name}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load configuration: {config_name}")
    
    def save_gem_configuration(self):
        """Save current gem configuration to file."""
        if not self.controller.current_gem_config:
            QMessageBox.warning(self, "Save Configuration", "No configuration to save. Please create a new configuration first.")
            return

        if self.controller.save_gem_configuration():
            QMessageBox.information(self, "Save Configuration", "Configuration saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save configuration.")
    
    def show_settings(self):
        """Show the settings dialog."""
        if self.settings_widget is None:
            self.settings_widget = SettingsWidget(self.config_service, self)
        
        self.settings_widget.show()
        self.settings_widget.raise_()
        self.settings_widget.activateWindow()
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Custom Gemini Agent GUI",
            "Custom Gemini Agent GUI v1.0.0\n\n"
            "A powerful desktop interface for Google Gemini API\n"
            "with custom RAG capabilities.\n\n"
            "Built with PyQt6 and Python."
        )
    
    def load_session_state(self):
        """Load the last session state."""
        try:
            # Load last configuration if available
            if self.controller.current_gem_config:
                config = self.controller.current_gem_config
                self.instructions_widget.set_agent_name(config.name)
                self.instructions_widget.set_instructions(config.instructions)
            logger.info("Session state loaded")
        except Exception as e:
            logger.warning(f"Failed to load session state: {e}")
    
    def save_session_state(self):
        """Save the current session state."""
        try:
            # Auto-save current configuration
            if self.controller.current_gem_config:
                self.controller.save_gem_configuration()
            logger.info("Session state saved")
        except Exception as e:
            logger.warning(f"Failed to save session state: {e}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        self.save_session_state()
        logger.info("Application closing")
        event.accept()
