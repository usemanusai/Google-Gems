"""
Settings Widget

Widget for managing application settings including API keys.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox,
    QTabWidget, QWidget, QSpinBox, QCheckBox,
    QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from loguru import logger

from services.config_service import ConfigService


class SettingsWidget(QDialog):
    """Settings dialog widget."""
    
    def __init__(self, config_service: ConfigService, parent=None):
        super().__init__(parent)
        self.config_service = config_service
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # API Settings tab
        api_tab = self.create_api_tab()
        tab_widget.addTab(api_tab, "API Settings")
        
        # General Settings tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Advanced Settings tab
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Advanced")
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test API Connection")
        self.test_button.clicked.connect(self.test_api_connection)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        logger.debug("SettingsWidget initialized")
    
    def create_api_tab(self):
        """Create the API settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Google Gemini API section
        gemini_group = QGroupBox("Google Gemini API")
        gemini_layout = QFormLayout(gemini_group)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your Google Gemini API key...")
        
        self.show_api_key_checkbox = QCheckBox("Show API key")
        self.show_api_key_checkbox.toggled.connect(self.toggle_api_key_visibility)
        
        gemini_layout.addRow("API Key:", self.api_key_edit)
        gemini_layout.addRow("", self.show_api_key_checkbox)
        
        layout.addWidget(gemini_group)
        
        # API Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setMaximumHeight(120)
        instructions_text.setPlainText(
            "To get your Google Gemini API key:\n"
            "1. Go to https://makersuite.google.com/app/apikey\n"
            "2. Sign in with your Google account\n"
            "3. Click 'Create API Key'\n"
            "4. Copy the generated key and paste it above\n\n"
            "Your API key will be stored securely in your system's credential manager."
        )
        instructions_layout.addWidget(instructions_text)
        
        layout.addWidget(instructions_group)
        layout.addStretch()
        
        return widget
    
    def create_general_tab(self):
        """Create the general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # UI Settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.auto_save_checkbox = QCheckBox("Auto-save configurations")
        self.auto_save_checkbox.setChecked(True)
        
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(60, 3600)
        self.auto_save_interval_spin.setValue(300)
        self.auto_save_interval_spin.setSuffix(" seconds")
        
        ui_layout.addRow("", self.auto_save_checkbox)
        ui_layout.addRow("Auto-save interval:", self.auto_save_interval_spin)
        
        layout.addWidget(ui_group)
        
        # Chat Settings
        chat_group = QGroupBox("Chat")
        chat_layout = QFormLayout(chat_group)
        
        self.max_history_spin = QSpinBox()
        self.max_history_spin.setRange(100, 10000)
        self.max_history_spin.setValue(1000)
        
        chat_layout.addRow("Max chat history:", self.max_history_spin)
        
        layout.addWidget(chat_group)
        layout.addStretch()
        
        return widget
    
    def create_advanced_tab(self):
        """Create the advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # RAG Settings
        rag_group = QGroupBox("RAG (Retrieval-Augmented Generation)")
        rag_layout = QFormLayout(rag_group)
        
        self.embedding_model_edit = QLineEdit()
        self.embedding_model_edit.setText("msmarco-MiniLM-L-6-v3")
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 5000)
        self.chunk_size_spin.setValue(1000)
        
        self.chunk_overlap_spin = QSpinBox()
        self.chunk_overlap_spin.setRange(0, 1000)
        self.chunk_overlap_spin.setValue(200)
        
        rag_layout.addRow("Embedding model:", self.embedding_model_edit)
        rag_layout.addRow("Chunk size:", self.chunk_size_spin)
        rag_layout.addRow("Chunk overlap:", self.chunk_overlap_spin)
        
        layout.addWidget(rag_group)
        
        # Debug Settings
        debug_group = QGroupBox("Debug")
        debug_layout = QFormLayout(debug_group)
        
        self.debug_logging_checkbox = QCheckBox("Enable debug logging")
        debug_layout.addRow("", self.debug_logging_checkbox)
        
        layout.addWidget(debug_group)
        layout.addStretch()
        
        return widget
    
    def toggle_api_key_visibility(self, checked):
        """Toggle API key visibility."""
        if checked:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def load_settings(self):
        """Load settings from config service."""
        try:
            # Load API key
            api_key = self.config_service.get_api_key()
            if api_key:
                self.api_key_edit.setText(api_key)
            
            # Load other settings
            settings = self.config_service.settings
            
            self.auto_save_interval_spin.setValue(settings.auto_save_interval)
            self.max_history_spin.setValue(settings.max_chat_history)
            self.embedding_model_edit.setText(settings.embedding_model)
            self.chunk_size_spin.setValue(settings.chunk_size)
            self.chunk_overlap_spin.setValue(settings.chunk_overlap)
            
            logger.debug("Settings loaded")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    def save_settings(self):
        """Save settings to config service."""
        try:
            # Save API key
            api_key = self.api_key_edit.text().strip()
            if api_key:
                self.config_service.set_api_key(api_key)
            
            # Save other settings
            settings = self.config_service.settings
            settings.auto_save_interval = self.auto_save_interval_spin.value()
            settings.max_chat_history = self.max_history_spin.value()
            settings.embedding_model = self.embedding_model_edit.text().strip()
            settings.chunk_size = self.chunk_size_spin.value()
            settings.chunk_overlap = self.chunk_overlap_spin.value()
            
            # Save to file
            if self.config_service.save_settings():
                QMessageBox.information(self, "Settings", "Settings saved successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Settings", "Failed to save settings.")
            
            logger.info("Settings saved")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def test_api_connection(self):
        """Test the API connection."""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Test API", "Please enter an API key first.")
            return
        
        # TODO: Implement actual API test
        QMessageBox.information(
            self, 
            "Test API", 
            "API connection test will be implemented in the next update."
        )
        logger.info("API connection test requested")
    
    def reset_to_defaults(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.auto_save_interval_spin.setValue(300)
            self.max_history_spin.setValue(1000)
            self.embedding_model_edit.setText("msmarco-MiniLM-L-6-v3")
            self.chunk_size_spin.setValue(1000)
            self.chunk_overlap_spin.setValue(200)
            self.debug_logging_checkbox.setChecked(False)
            
            logger.info("Settings reset to defaults")
