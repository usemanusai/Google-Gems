"""
Configuration Manager Widget

Advanced configuration management interface for Epic 5.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QLineEdit, QTextEdit, QComboBox, QGroupBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QDialog,
    QFormLayout, QSpinBox, QCheckBox, QMessageBox,
    QFileDialog, QProgressBar, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QColor, QFont
from loguru import logger
from typing import List, Dict, Any, Optional


class ConfigurationManagerWidget(QWidget):
    """Widget for advanced configuration management."""
    
    # Signals
    configuration_selected = pyqtSignal(str)  # config_id
    workspace_changed = pyqtSignal(str)  # workspace_id
    template_applied = pyqtSignal(str, str)  # template_name, config_name
    import_requested = pyqtSignal(str)  # file_path
    export_requested = pyqtSignal(list)  # config_ids
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_workspace_id = "default"
        self.configurations = []
        self.workspaces = []
        self.templates = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Configurations tab
        self.configurations_tab = self.create_configurations_tab()
        self.tab_widget.addTab(self.configurations_tab, "Configurations")
        
        # Workspaces tab
        self.workspaces_tab = self.create_workspaces_tab()
        self.tab_widget.addTab(self.workspaces_tab, "Workspaces")
        
        # Templates tab
        self.templates_tab = self.create_templates_tab()
        self.tab_widget.addTab(self.templates_tab, "Templates")
        
        # Import/Export tab
        self.import_export_tab = self.create_import_export_tab()
        self.tab_widget.addTab(self.import_export_tab, "Import/Export")
        
        layout.addWidget(self.tab_widget)
    
    def create_configurations_tab(self) -> QWidget:
        """Create the configurations management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Workspace selector
        workspace_layout = QHBoxLayout()
        workspace_layout.addWidget(QLabel("Workspace:"))
        
        self.workspace_combo = QComboBox()
        self.workspace_combo.currentTextChanged.connect(self.on_workspace_changed)
        workspace_layout.addWidget(self.workspace_combo)
        
        workspace_layout.addStretch()
        layout.addLayout(workspace_layout)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search configurations...")
        self.search_edit.textChanged.connect(self.filter_configurations)
        search_layout.addWidget(self.search_edit)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.filter_configurations)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Configuration list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        self.config_list = QListWidget()
        self.config_list.itemClicked.connect(self.on_configuration_selected)
        self.config_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.config_list.customContextMenuRequested.connect(self.show_config_context_menu)
        list_layout.addWidget(self.config_list)
        
        # Configuration list buttons
        list_buttons = QHBoxLayout()
        
        self.new_config_button = QPushButton("New")
        self.new_config_button.clicked.connect(self.create_new_configuration)
        list_buttons.addWidget(self.new_config_button)
        
        self.duplicate_button = QPushButton("Duplicate")
        self.duplicate_button.clicked.connect(self.duplicate_configuration)
        self.duplicate_button.setEnabled(False)
        list_buttons.addWidget(self.duplicate_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_configuration)
        self.delete_button.setEnabled(False)
        list_buttons.addWidget(self.delete_button)
        
        list_layout.addLayout(list_buttons)
        splitter.addWidget(list_widget)
        
        # Configuration details
        details_widget = self.create_configuration_details_widget()
        splitter.addWidget(details_widget)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        return tab
    
    def create_configuration_details_widget(self) -> QWidget:
        """Create the configuration details widget."""
        widget = QGroupBox("Configuration Details")
        layout = QVBoxLayout(widget)
        
        # Basic info
        form_layout = QFormLayout()
        
        self.config_name_edit = QLineEdit()
        form_layout.addRow("Name:", self.config_name_edit)
        
        self.config_description_edit = QLineEdit()
        form_layout.addRow("Description:", self.config_description_edit)
        
        self.config_category_edit = QLineEdit()
        form_layout.addRow("Category:", self.config_category_edit)
        
        layout.addLayout(form_layout)
        
        # Instructions
        layout.addWidget(QLabel("Instructions:"))
        self.config_instructions_edit = QTextEdit()
        self.config_instructions_edit.setMaximumHeight(150)
        layout.addWidget(self.config_instructions_edit)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.usage_count_label = QLabel("0")
        stats_layout.addRow("Usage Count:", self.usage_count_label)
        
        self.message_count_label = QLabel("0")
        stats_layout.addRow("Messages:", self.message_count_label)
        
        self.created_label = QLabel("-")
        stats_layout.addRow("Created:", self.created_label)
        
        self.modified_label = QLabel("-")
        stats_layout.addRow("Modified:", self.modified_label)
        
        layout.addWidget(stats_group)
        
        # Action buttons
        action_buttons = QHBoxLayout()
        
        self.save_config_button = QPushButton("Save")
        self.save_config_button.clicked.connect(self.save_configuration_changes)
        action_buttons.addWidget(self.save_config_button)
        
        self.revert_button = QPushButton("Revert")
        self.revert_button.clicked.connect(self.revert_configuration_changes)
        action_buttons.addWidget(self.revert_button)
        
        action_buttons.addStretch()
        layout.addLayout(action_buttons)
        
        return widget
    
    def create_workspaces_tab(self) -> QWidget:
        """Create the workspaces management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Workspace list
        self.workspace_list = QListWidget()
        self.workspace_list.itemClicked.connect(self.on_workspace_selected)
        layout.addWidget(self.workspace_list)
        
        # Workspace buttons
        workspace_buttons = QHBoxLayout()
        
        self.new_workspace_button = QPushButton("New Workspace")
        self.new_workspace_button.clicked.connect(self.create_new_workspace)
        workspace_buttons.addWidget(self.new_workspace_button)
        
        self.edit_workspace_button = QPushButton("Edit")
        self.edit_workspace_button.clicked.connect(self.edit_workspace)
        self.edit_workspace_button.setEnabled(False)
        workspace_buttons.addWidget(self.edit_workspace_button)
        
        self.delete_workspace_button = QPushButton("Delete")
        self.delete_workspace_button.clicked.connect(self.delete_workspace)
        self.delete_workspace_button.setEnabled(False)
        workspace_buttons.addWidget(self.delete_workspace_button)
        
        workspace_buttons.addStretch()
        layout.addLayout(workspace_buttons)
        
        return tab
    
    def create_templates_tab(self) -> QWidget:
        """Create the templates management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Template category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        
        self.template_category_filter = QComboBox()
        self.template_category_filter.addItem("All Categories")
        self.template_category_filter.currentTextChanged.connect(self.filter_templates)
        category_layout.addWidget(self.template_category_filter)
        
        category_layout.addStretch()
        layout.addLayout(category_layout)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)
        
        # Template buttons
        template_buttons = QHBoxLayout()
        
        self.apply_template_button = QPushButton("Apply Template")
        self.apply_template_button.clicked.connect(self.apply_template)
        self.apply_template_button.setEnabled(False)
        template_buttons.addWidget(self.apply_template_button)
        
        self.create_template_button = QPushButton("Create from Config")
        self.create_template_button.clicked.connect(self.create_template_from_config)
        template_buttons.addWidget(self.create_template_button)
        
        self.delete_template_button = QPushButton("Delete")
        self.delete_template_button.clicked.connect(self.delete_template)
        self.delete_template_button.setEnabled(False)
        template_buttons.addWidget(self.delete_template_button)
        
        template_buttons.addStretch()
        layout.addLayout(template_buttons)
        
        return tab
    
    def create_import_export_tab(self) -> QWidget:
        """Create the import/export tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export section
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout(export_group)
        
        export_buttons = QHBoxLayout()
        
        self.export_selected_button = QPushButton("Export Selected")
        self.export_selected_button.clicked.connect(self.export_selected_configurations)
        export_buttons.addWidget(self.export_selected_button)
        
        self.export_workspace_button = QPushButton("Export Workspace")
        self.export_workspace_button.clicked.connect(self.export_current_workspace)
        export_buttons.addWidget(self.export_workspace_button)
        
        self.create_backup_button = QPushButton("Create Backup")
        self.create_backup_button.clicked.connect(self.create_backup)
        export_buttons.addWidget(self.create_backup_button)
        
        export_layout.addLayout(export_buttons)
        layout.addWidget(export_group)
        
        # Import section
        import_group = QGroupBox("Import")
        import_layout = QVBoxLayout(import_group)
        
        import_buttons = QHBoxLayout()
        
        self.import_file_button = QPushButton("Import from File")
        self.import_file_button.clicked.connect(self.import_from_file)
        import_buttons.addWidget(self.import_file_button)
        
        self.restore_backup_button = QPushButton("Restore Backup")
        self.restore_backup_button.clicked.connect(self.restore_backup)
        import_buttons.addWidget(self.restore_backup_button)
        
        import_layout.addLayout(import_buttons)
        
        # Import progress
        self.import_progress = QProgressBar()
        self.import_progress.setVisible(False)
        import_layout.addWidget(self.import_progress)
        
        layout.addWidget(import_group)
        
        # Export history
        history_group = QGroupBox("Export History")
        history_layout = QVBoxLayout(history_group)
        
        self.export_history_table = QTableWidget()
        self.export_history_table.setColumnCount(4)
        self.export_history_table.setHorizontalHeaderLabels(["Filename", "Size", "Created", "Type"])
        history_layout.addWidget(self.export_history_table)
        
        layout.addWidget(history_group)
        
        layout.addStretch()
        return tab
    
    def update_configurations(self, configurations: List[Dict[str, Any]]):
        """Update the configurations list."""
        self.configurations = configurations
        self.refresh_configuration_list()
    
    def update_workspaces(self, workspaces: List[Dict[str, Any]]):
        """Update the workspaces list."""
        self.workspaces = workspaces
        self.refresh_workspace_list()
        self.refresh_workspace_combo()
    
    def update_templates(self, templates: List[Dict[str, Any]]):
        """Update the templates list."""
        self.templates = templates
        self.refresh_template_list()
        self.refresh_template_categories()
    
    def refresh_configuration_list(self):
        """Refresh the configuration list display."""
        self.config_list.clear()
        
        # Filter configurations by current workspace
        workspace_configs = [
            config for config in self.configurations
            if self.current_workspace_id == "all" or 
               config.get("workspace_id") == self.current_workspace_id
        ]
        
        # Apply search and category filters
        search_text = self.search_edit.text().lower()
        category_filter = self.category_filter.currentText()
        
        for config in workspace_configs:
            # Apply filters
            if search_text and search_text not in config.get("name", "").lower():
                continue
            
            if category_filter != "All Categories" and config.get("category") != category_filter:
                continue
            
            # Create list item
            item = QListWidgetItem(config.get("name", "Unnamed"))
            item.setData(Qt.ItemDataRole.UserRole, config)
            
            # Add visual indicators
            if config.get("is_shared", False):
                item.setIcon(QIcon("shared"))  # Would need actual icon
            
            self.config_list.addItem(item)
    
    def refresh_workspace_list(self):
        """Refresh the workspace list display."""
        self.workspace_list.clear()
        
        for workspace in self.workspaces:
            item = QListWidgetItem(workspace.get("name", "Unnamed"))
            item.setData(Qt.ItemDataRole.UserRole, workspace)
            self.workspace_list.addItem(item)
    
    def refresh_workspace_combo(self):
        """Refresh the workspace combo box."""
        self.workspace_combo.clear()
        self.workspace_combo.addItem("All Workspaces", "all")
        
        for workspace in self.workspaces:
            self.workspace_combo.addItem(workspace.get("name", "Unnamed"), workspace.get("id"))
    
    def refresh_template_list(self):
        """Refresh the template list display."""
        self.template_list.clear()
        
        category_filter = self.template_category_filter.currentText()
        
        for template in self.templates:
            # Apply category filter
            if category_filter != "All Categories" and template.get("category") != category_filter:
                continue
            
            item = QListWidgetItem(template.get("name", "Unnamed"))
            item.setData(Qt.ItemDataRole.UserRole, template)
            
            # Mark built-in templates
            if template.get("is_builtin", False):
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.template_list.addItem(item)
    
    def refresh_template_categories(self):
        """Refresh template category filter."""
        current_category = self.template_category_filter.currentText()
        self.template_category_filter.clear()
        self.template_category_filter.addItem("All Categories")
        
        categories = set(template.get("category", "general") for template in self.templates)
        for category in sorted(categories):
            self.template_category_filter.addItem(category)
        
        # Restore selection if possible
        index = self.template_category_filter.findText(current_category)
        if index >= 0:
            self.template_category_filter.setCurrentIndex(index)
    
    # Signal handlers (placeholder implementations)
    def on_workspace_changed(self, workspace_name: str):
        """Handle workspace change."""
        # Find workspace ID by name
        for workspace in self.workspaces:
            if workspace.get("name") == workspace_name:
                self.current_workspace_id = workspace.get("id", "default")
                break
        else:
            self.current_workspace_id = "all"
        
        self.refresh_configuration_list()
        self.workspace_changed.emit(self.current_workspace_id)
    
    def on_configuration_selected(self, item: QListWidgetItem):
        """Handle configuration selection."""
        config = item.data(Qt.ItemDataRole.UserRole)
        if config:
            self.load_configuration_details(config)
            self.configuration_selected.emit(config.get("id", ""))
    
    def on_workspace_selected(self, item: QListWidgetItem):
        """Handle workspace selection."""
        self.edit_workspace_button.setEnabled(True)
        self.delete_workspace_button.setEnabled(True)
    
    def on_template_selected(self, item: QListWidgetItem):
        """Handle template selection."""
        template = item.data(Qt.ItemDataRole.UserRole)
        self.apply_template_button.setEnabled(True)
        
        # Don't allow deleting built-in templates
        is_builtin = template.get("is_builtin", False) if template else False
        self.delete_template_button.setEnabled(not is_builtin)
    
    def load_configuration_details(self, config: Dict[str, Any]):
        """Load configuration details into the form."""
        self.config_name_edit.setText(config.get("name", ""))
        self.config_description_edit.setText(config.get("description", ""))
        self.config_category_edit.setText(config.get("category", ""))
        self.config_instructions_edit.setText(config.get("instructions", ""))
        
        # Update statistics
        self.usage_count_label.setText(str(config.get("usage_count", 0)))
        self.message_count_label.setText(str(config.get("total_messages", 0)))
        self.created_label.setText(config.get("created_at", "-"))
        self.modified_label.setText(config.get("modified_at", "-"))
    
    # Placeholder methods for actions
    def filter_configurations(self):
        """Filter configurations based on search and category."""
        self.refresh_configuration_list()
    
    def filter_templates(self):
        """Filter templates based on category."""
        self.refresh_template_list()
    
    def create_new_configuration(self):
        """Create a new configuration."""
        pass  # Will be implemented by controller
    
    def duplicate_configuration(self):
        """Duplicate selected configuration."""
        pass  # Will be implemented by controller
    
    def delete_configuration(self):
        """Delete selected configuration."""
        pass  # Will be implemented by controller
    
    def save_configuration_changes(self):
        """Save changes to current configuration."""
        pass  # Will be implemented by controller
    
    def revert_configuration_changes(self):
        """Revert changes to current configuration."""
        pass  # Will be implemented by controller
    
    def create_new_workspace(self):
        """Create a new workspace."""
        pass  # Will be implemented by controller
    
    def edit_workspace(self):
        """Edit selected workspace."""
        pass  # Will be implemented by controller
    
    def delete_workspace(self):
        """Delete selected workspace."""
        pass  # Will be implemented by controller
    
    def apply_template(self):
        """Apply selected template."""
        pass  # Will be implemented by controller
    
    def create_template_from_config(self):
        """Create template from current configuration."""
        pass  # Will be implemented by controller
    
    def delete_template(self):
        """Delete selected template."""
        pass  # Will be implemented by controller
    
    def export_selected_configurations(self):
        """Export selected configurations."""
        pass  # Will be implemented by controller
    
    def export_current_workspace(self):
        """Export current workspace."""
        pass  # Will be implemented by controller
    
    def create_backup(self):
        """Create a backup."""
        pass  # Will be implemented by controller
    
    def import_from_file(self):
        """Import from file."""
        pass  # Will be implemented by controller
    
    def restore_backup(self):
        """Restore from backup."""
        pass  # Will be implemented by controller
    
    def show_config_context_menu(self, position):
        """Show context menu for configuration list."""
        pass  # Will be implemented with QMenu
