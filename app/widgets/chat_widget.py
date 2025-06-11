"""
Chat Widget

Widget for displaying chat conversation and handling user input.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QGroupBox, QSplitter, QLabel,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor
from loguru import logger
from datetime import datetime


class ChatWidget(QWidget):
    """Widget for chat interface."""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create group box
        group_box = QGroupBox("Chat / Preview")
        group_layout = QVBoxLayout(group_box)
        
        # Create splitter for chat area and input
        splitter = QSplitter(Qt.Orientation.Vertical)
        group_layout.addWidget(splitter)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        self.chat_display.setPlaceholderText(
            "Chat conversation will appear here...\n\n"
            "Enter your message below and click 'Send' or press Ctrl+Enter to start chatting."
        )
        splitter.addWidget(self.chat_display)
        
        # Input area
        input_widget = self.create_input_area()
        splitter.addWidget(input_widget)
        
        # Set splitter proportions (chat area larger)
        splitter.setSizes([600, 200])
        
        layout.addWidget(group_box)
        
        # Add welcome message
        self.add_system_message("Welcome to Custom Gemini Agent GUI! Configure your agent and start chatting.")
        
        logger.debug("ChatWidget initialized")
    
    def create_input_area(self):
        """Create the input area widget."""
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Input text area
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(120)
        self.input_text.setPlaceholderText("Type your message here... (Ctrl+Enter to send)")
        self.input_text.installEventFilter(self)
        input_layout.addWidget(self.input_text)
        
        # Button area
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setDefault(True)
        
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_generation)
        self.stop_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.send_button)
        
        input_layout.addLayout(button_layout)
        
        return input_widget
    
    def eventFilter(self, obj, event):
        """Handle keyboard events for input text area."""
        if obj == self.input_text and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.send_message()
                    return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        """Send a message."""
        message = self.input_text.toPlainText().strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_user_message(message)
        
        # Clear input
        self.input_text.clear()
        
        # Emit signal
        self.message_sent.emit(message)
        
        # Update UI state
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        logger.info(f"Message sent: {message[:50]}...")
    
    def add_user_message(self, message: str):
        """Add a user message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.append(f"<div style='margin-bottom: 10px;'>")
        self.chat_display.append(f"<b style='color: #2196F3;'>[{timestamp}] You:</b>")
        self.chat_display.append(f"<div style='margin-left: 20px; background-color: #f5f5f5; padding: 8px; border-radius: 5px;'>")
        self.chat_display.append(message.replace('\n', '<br>'))
        self.chat_display.append(f"</div></div>")
        
        # Scroll to bottom
        self.scroll_to_bottom()
        
        # Add to history
        self.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": timestamp
        })
    
    def add_assistant_message(self, message: str):
        """Add an assistant message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.append(f"<div style='margin-bottom: 10px;'>")
        self.chat_display.append(f"<b style='color: #4CAF50;'>[{timestamp}] Assistant:</b>")
        self.chat_display.append(f"<div style='margin-left: 20px; background-color: #e8f5e8; padding: 8px; border-radius: 5px;'>")
        self.chat_display.append(message.replace('\n', '<br>'))
        self.chat_display.append(f"</div></div>")
        
        # Scroll to bottom
        self.scroll_to_bottom()
        
        # Add to history
        self.chat_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": timestamp
        })
        
        # Update UI state
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def add_system_message(self, message: str):
        """Add a system message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.append(f"<div style='margin-bottom: 10px;'>")
        self.chat_display.append(f"<i style='color: #666;'>[{timestamp}] System: {message}</i>")
        self.chat_display.append(f"</div>")
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def add_error_message(self, message: str):
        """Add an error message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.append(f"<div style='margin-bottom: 10px;'>")
        self.chat_display.append(f"<b style='color: #f44336;'>[{timestamp}] Error:</b>")
        self.chat_display.append(f"<div style='margin-left: 20px; background-color: #ffebee; padding: 8px; border-radius: 5px; color: #c62828;'>")
        self.chat_display.append(message.replace('\n', '<br>'))
        self.chat_display.append(f"</div></div>")
        
        # Scroll to bottom
        self.scroll_to_bottom()
        
        # Update UI state
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def scroll_to_bottom(self):
        """Scroll the chat display to the bottom."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
    
    def clear_chat(self):
        """Clear the chat display and history."""
        self.chat_display.clear()
        self.chat_history.clear()
        self.add_system_message("Chat cleared.")
        logger.info("Chat cleared")
    
    def stop_generation(self):
        """Stop the current generation."""
        # TODO: Implement stop generation logic
        self.add_system_message("Generation stopped.")
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        logger.info("Generation stopped")
    
    def get_chat_history(self) -> list:
        """Get the chat history."""
        return self.chat_history.copy()
    
    def set_chat_history(self, history: list):
        """Set the chat history and update display."""
        self.chat_history = history.copy()
        self.chat_display.clear()
        
        for entry in self.chat_history:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            timestamp = entry.get("timestamp", "")
            
            if role == "user":
                self.chat_display.append(f"<div style='margin-bottom: 10px;'>")
                self.chat_display.append(f"<b style='color: #2196F3;'>[{timestamp}] You:</b>")
                self.chat_display.append(f"<div style='margin-left: 20px; background-color: #f5f5f5; padding: 8px; border-radius: 5px;'>")
                self.chat_display.append(content.replace('\n', '<br>'))
                self.chat_display.append(f"</div></div>")
            elif role == "assistant":
                self.chat_display.append(f"<div style='margin-bottom: 10px;'>")
                self.chat_display.append(f"<b style='color: #4CAF50;'>[{timestamp}] Assistant:</b>")
                self.chat_display.append(f"<div style='margin-left: 20px; background-color: #e8f5e8; padding: 8px; border-radius: 5px;'>")
                self.chat_display.append(content.replace('\n', '<br>'))
                self.chat_display.append(f"</div></div>")
        
        self.scroll_to_bottom()
