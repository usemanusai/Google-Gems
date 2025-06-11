"""
Instructions Widget

Widget for entering and managing agent instructions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLabel, QLineEdit, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from loguru import logger


class InstructionsWidget(QWidget):
    """Widget for managing agent instructions."""
    
    instructions_changed = pyqtSignal(str)
    agent_name_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create group box
        group_box = QGroupBox("Agent Configuration")
        group_layout = QVBoxLayout(group_box)
        
        # Agent name section
        name_layout = QHBoxLayout()
        name_label = QLabel("Agent Name:")
        name_label.setMinimumWidth(80)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter agent name...")
        self.name_edit.textChanged.connect(self.on_name_changed)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        group_layout.addLayout(name_layout)
        
        # Instructions section
        instructions_label = QLabel("Instructions:")
        group_layout.addWidget(instructions_label)
        
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setPlaceholderText(
            "Enter detailed instructions for your AI agent...\n\n"
            "Example:\n"
            "You are a helpful assistant specialized in Python programming. "
            "Always provide clear, well-commented code examples and explain "
            "your reasoning step by step."
        )
        self.instructions_edit.textChanged.connect(self.on_instructions_changed)
        group_layout.addWidget(self.instructions_edit)
        
        # Buttons section
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_instructions)
        
        self.load_template_button = QPushButton("Load Template")
        self.load_template_button.clicked.connect(self.load_template)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.load_template_button)
        button_layout.addStretch()
        
        group_layout.addLayout(button_layout)
        
        layout.addWidget(group_box)
        
        logger.debug("InstructionsWidget initialized")
    
    def on_name_changed(self):
        """Handle agent name change."""
        name = self.name_edit.text().strip()
        self.agent_name_changed.emit(name)
        logger.debug(f"Agent name changed to: {name}")
    
    def on_instructions_changed(self):
        """Handle instructions text change."""
        instructions = self.instructions_edit.toPlainText()
        self.instructions_changed.emit(instructions)
        logger.debug("Instructions changed")
    
    def clear_instructions(self):
        """Clear the instructions text."""
        self.instructions_edit.clear()
        logger.debug("Instructions cleared")
    
    def load_template(self):
        """Load an instruction template."""
        # TODO: Implement template loading
        logger.info("Load template requested")
    
    def get_agent_name(self) -> str:
        """Get the current agent name."""
        return self.name_edit.text().strip()
    
    def set_agent_name(self, name: str):
        """Set the agent name."""
        self.name_edit.setText(name)
    
    def get_instructions(self) -> str:
        """Get the current instructions."""
        return self.instructions_edit.toPlainText()
    
    def set_instructions(self, instructions: str):
        """Set the instructions text."""
        self.instructions_edit.setPlainText(instructions)
    
    def clear_all(self):
        """Clear both name and instructions."""
        self.name_edit.clear()
        self.instructions_edit.clear()
