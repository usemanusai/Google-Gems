"""
Knowledge Widget

Widget for managing knowledge sources and file ingestion.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QLabel, QPushButton, QGroupBox, QListWidgetItem,
    QFileDialog, QMessageBox, QInputDialog, QMenu,
    QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor
from loguru import logger
from pathlib import Path


class KnowledgeWidget(QWidget):
    """Widget for managing knowledge sources."""
    
    knowledge_sources_changed = pyqtSignal(list)
    monitoring_toggle_requested = pyqtSignal(str)  # source_id
    reindex_requested = pyqtSignal()
    batch_process_requested = pyqtSignal(list)  # sources
    google_drive_auth_requested = pyqtSignal()
    url_source_requested = pyqtSignal(str, dict)  # url, config
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.knowledge_sources = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create group box
        group_box = QGroupBox("Knowledge Base")
        group_layout = QVBoxLayout(group_box)
        
        # File list
        list_label = QLabel("Knowledge Sources:")
        group_layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        group_layout.addWidget(self.file_list)
        
        # Buttons section
        button_layout = QVBoxLayout()
        
        # Add files buttons
        add_files_layout = QHBoxLayout()
        
        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.add_files)
        
        self.add_folder_button = QPushButton("Add Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        
        add_files_layout.addWidget(self.add_files_button)
        add_files_layout.addWidget(self.add_folder_button)
        button_layout.addLayout(add_files_layout)
        
        # Advanced sources buttons
        advanced_layout = QHBoxLayout()
        
        self.add_github_button = QPushButton("Add GitHub Repo")
        self.add_github_button.clicked.connect(self.add_github_repo)
        
        self.add_gdrive_button = QPushButton("Add Google Drive")
        self.add_gdrive_button.clicked.connect(self.add_google_drive)

        self.add_url_button = QPushButton("Add URL/Website")
        self.add_url_button.clicked.connect(self.add_url)
        
        advanced_layout.addWidget(self.add_github_button)
        advanced_layout.addWidget(self.add_gdrive_button)
        button_layout.addLayout(advanced_layout)

        # Web sources layout
        web_layout = QHBoxLayout()
        web_layout.addWidget(self.add_url_button)

        self.batch_process_button = QPushButton("Batch Process")
        self.batch_process_button.clicked.connect(self.batch_process_sources)
        web_layout.addWidget(self.batch_process_button)

        button_layout.addLayout(web_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected)
        self.remove_button.setEnabled(False)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_sources)

        self.reindex_button = QPushButton("Reindex All")
        self.reindex_button.clicked.connect(self.reindex_all)

        control_layout.addWidget(self.remove_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.reindex_button)
        button_layout.addLayout(control_layout)

        # Monitoring controls
        monitoring_layout = QHBoxLayout()

        self.auto_monitor_checkbox = QCheckBox("Auto-monitor file changes")
        self.auto_monitor_checkbox.setChecked(True)

        monitoring_layout.addWidget(self.auto_monitor_checkbox)
        monitoring_layout.addStretch()
        button_layout.addLayout(monitoring_layout)
        
        group_layout.addLayout(button_layout)
        
        # Connect selection change
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(group_box)
        
        logger.debug("KnowledgeWidget initialized")
    
    def show_context_menu(self, position):
        """Show context menu for file list."""
        item = self.file_list.itemAt(position)
        if item is None:
            return
        
        menu = QMenu(self)
        
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)

        # Add monitoring toggle if applicable
        source_info = item.data(Qt.ItemDataRole.UserRole)
        if source_info and source_info.get("type") in ["file", "folder"]:
            menu.addSeparator()

            monitor_action = QAction("Toggle Monitoring", self)
            monitor_action.triggered.connect(lambda: self.toggle_monitoring(item))
            menu.addAction(monitor_action)
        
        menu.exec(self.file_list.mapToGlobal(position))
    
    def on_selection_changed(self):
        """Handle selection change in file list."""
        has_selection = len(self.file_list.selectedItems()) > 0
        self.remove_button.setEnabled(has_selection)
    
    def add_files(self):
        """Add individual files to knowledge base."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(
            "Documents (*.txt *.md *.pdf *.docx *.doc);;Code Files (*.py *.js *.html *.css *.json);;All Files (*)"
        )
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file_path in files:
                self.add_knowledge_source(file_path, "file")
            logger.info(f"Added {len(files)} files to knowledge base")
    
    def add_folder(self):
        """Add a folder to knowledge base."""
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        
        if folder_dialog.exec():
            folder_path = folder_dialog.selectedFiles()[0]
            self.add_knowledge_source(folder_path, "folder")
            logger.info(f"Added folder to knowledge base: {folder_path}")
    
    def add_github_repo(self):
        """Add a GitHub repository to knowledge base."""
        repo_url, ok = QInputDialog.getText(
            self, 
            "Add GitHub Repository", 
            "Enter GitHub repository URL:",
            text="https://github.com/user/repo"
        )
        
        if ok and repo_url.strip():
            self.add_knowledge_source(repo_url.strip(), "github")
            logger.info(f"Added GitHub repo to knowledge base: {repo_url}")
    
    def add_google_drive(self):
        """Add Google Drive folder to knowledge base."""
        folder_url, ok = QInputDialog.getText(
            self,
            "Add Google Drive Folder",
            "Enter Google Drive folder URL:",
            text="https://drive.google.com/drive/folders/..."
        )

        if ok and folder_url.strip():
            # First check if authentication is needed
            self.google_drive_auth_requested.emit()

            # Add the source
            self.add_knowledge_source(folder_url.strip(), "google_drive")
            logger.info(f"Added Google Drive folder: {folder_url}")

    def add_url(self):
        """Add URL or website to knowledge base."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Add URL/Website")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # URL input
        url_edit = QLineEdit()
        url_edit.setPlaceholderText("https://example.com")
        form_layout.addRow("URL:", url_edit)

        # Crawl mode
        crawl_mode_combo = QComboBox()
        crawl_mode_combo.addItems(["Single Page", "Crawl Website", "From Sitemap"])
        form_layout.addRow("Mode:", crawl_mode_combo)

        # Max pages
        max_pages_spin = QSpinBox()
        max_pages_spin.setRange(1, 100)
        max_pages_spin.setValue(10)
        form_layout.addRow("Max Pages:", max_pages_spin)

        # Same domain only
        same_domain_checkbox = QCheckBox("Same domain only")
        same_domain_checkbox.setChecked(True)
        form_layout.addRow("", same_domain_checkbox)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            url = url_edit.text().strip()
            if url:
                # Build configuration
                crawl_modes = {"Single Page": "single", "Crawl Website": "crawl", "From Sitemap": "sitemap"}
                config = {
                    "crawl_mode": crawl_modes[crawl_mode_combo.currentText()],
                    "max_pages": max_pages_spin.value(),
                    "same_domain_only": same_domain_checkbox.isChecked()
                }

                self.url_source_requested.emit(url, config)
                logger.info(f"Added URL source: {url} with config: {config}")

    def batch_process_sources(self):
        """Request batch processing of selected sources."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "Batch Processing",
                "Please select one or more sources to process."
            )
            return

        sources = []
        for item in selected_items:
            source_info = item.data(Qt.ItemDataRole.UserRole)
            if source_info:
                sources.append(source_info)

        if sources:
            reply = QMessageBox.question(
                self,
                "Batch Processing",
                f"Process {len(sources)} sources in batch mode?\n\n"
                "This will reprocess all selected sources using multiple workers.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.batch_process_requested.emit(sources)
                logger.info(f"Batch processing requested for {len(sources)} sources")
    
    def add_knowledge_source(self, source: str, source_type: str, source_id: str = None):
        """Add a knowledge source to the list."""
        import hashlib

        if not source_id:
            source_id = f"source_{len(self.knowledge_sources)}_{hashlib.md5(source.encode()).hexdigest()[:8]}"

        source_info = {
            "id": source_id,
            "path": source,
            "type": source_type,
            "status": "pending"
        }
        
        self.knowledge_sources.append(source_info)
        
        # Add to UI list
        display_text = f"[{source_type.upper()}] {Path(source).name if source_type in ['file', 'folder'] else source}"
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, source_info)
        self.file_list.addItem(item)
        
        # Emit signal
        self.knowledge_sources_changed.emit(self.knowledge_sources)
    
    def remove_selected(self):
        """Remove selected items from knowledge base."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            source_info = item.data(Qt.ItemDataRole.UserRole)
            if source_info in self.knowledge_sources:
                self.knowledge_sources.remove(source_info)
            
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
        
        logger.info(f"Removed {len(selected_items)} items from knowledge base")
        self.knowledge_sources_changed.emit(self.knowledge_sources)
    
    def clear_all(self):
        """Clear all knowledge sources."""
        reply = QMessageBox.question(
            self,
            "Clear Knowledge Base",
            "Are you sure you want to remove all knowledge sources?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.knowledge_sources.clear()
            self.file_list.clear()
            logger.info("Cleared all knowledge sources")
            self.knowledge_sources_changed.emit(self.knowledge_sources)
    
    def refresh_sources(self):
        """Refresh knowledge sources status."""
        logger.info("Refresh knowledge sources requested")
        # Emit signal to refresh - controller will handle the actual refresh
        self.knowledge_sources_changed.emit(self.knowledge_sources)

    def reindex_all(self):
        """Request reindexing of all sources."""
        reply = QMessageBox.question(
            self,
            "Reindex All Sources",
            "This will reprocess all knowledge sources. This may take some time. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Reindex all sources requested")
            self.reindex_requested.emit()

    def toggle_monitoring(self, item: QListWidgetItem):
        """Toggle monitoring for a specific source."""
        source_info = item.data(Qt.ItemDataRole.UserRole)
        if source_info:
            source_id = source_info.get("id")
            if source_id:
                self.monitoring_toggle_requested.emit(source_id)

    def update_source_status(self, source_id: str, status: str, is_monitoring: bool = False):
        """Update the visual status of a source."""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            source_info = item.data(Qt.ItemDataRole.UserRole)

            if source_info and source_info.get("id") == source_id:
                # Update the display text with status
                source_type = source_info.get("type", "unknown")
                source_path = source_info.get("path", "")

                display_text = f"[{source_type.upper()}] {Path(source_path).name if source_type in ['file', 'folder'] else source_path}"

                # Add status indicators
                if is_monitoring:
                    display_text += " 👁️"  # Eye emoji for monitoring

                if status == "processing":
                    display_text += " ⏳"  # Hourglass for processing
                elif status == "indexed":
                    display_text += " ✅"  # Check mark for indexed
                elif status == "error":
                    display_text += " ❌"  # X mark for error

                item.setText(display_text)

                # Update color based on status
                if status == "error":
                    item.setBackground(QColor(255, 200, 200))  # Light red
                elif status == "indexed":
                    item.setBackground(QColor(200, 255, 200))  # Light green
                elif status == "processing":
                    item.setBackground(QColor(255, 255, 200))  # Light yellow
                else:
                    item.setBackground(QColor(255, 255, 255))  # White

                break
    
    def get_knowledge_sources(self) -> list:
        """Get the current knowledge sources."""
        return self.knowledge_sources.copy()
    
    def set_knowledge_sources(self, sources: list):
        """Set the knowledge sources."""
        self.knowledge_sources = sources.copy()
        self.file_list.clear()
        
        for source_info in self.knowledge_sources:
            source_type = source_info.get("type", "unknown")
            source_path = source_info.get("path", "")
            
            display_text = f"[{source_type.upper()}] {Path(source_path).name if source_type in ['file', 'folder'] else source_path}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, source_info)
            self.file_list.addItem(item)

    def clear_all_sources(self):
        """Clear all knowledge sources programmatically."""
        self.knowledge_sources.clear()
        self.file_list.clear()
        self.knowledge_sources_changed.emit(self.knowledge_sources)
