# Development Guide

This document provides detailed information for developers working on the Custom Gemini Agent GUI project.

## Project Structure

```
Custom-Gemini-Agent-GUI/
├── app/                    # Main application code
│   ├── main.py            # Application entry point
│   ├── main_window.py     # Main window class
│   ├── controllers/       # MVC Controllers
│   │   └── main_controller.py
│   ├── models/           # Data models
│   │   └── knowledge_source.py
│   ├── services/         # Business logic services
│   │   ├── config_service.py
│   │   ├── api_service.py
│   │   └── rag_service.py
│   ├── ui/              # UI components
│   └── widgets/         # Custom PyQt6 widgets
│       ├── instructions_widget.py
│       ├── knowledge_widget.py
│       ├── chat_widget.py
│       └── settings_widget.py
├── assets/              # Static assets
├── docs/               # Documentation
├── tests/              # Test files
├── bmad-agent/         # BMAD methodology files
├── requirements.txt    # Python dependencies
├── run.py             # Application launcher
├── setup_dev.py       # Development setup script
└── build.py           # Build script
```

## Architecture Overview

The application follows a **Model-View-Controller (MVC)** pattern with a **Service-Oriented Architecture** for business logic:

### Models
- **KnowledgeSource**: Represents knowledge sources in the RAG system
- **GemConfiguration**: Represents saved agent configurations
- **AppSettings**: Application settings and preferences

### Views (Widgets)
- **MainWindow**: Primary application window
- **InstructionsWidget**: Agent configuration interface
- **KnowledgeWidget**: Knowledge source management
- **ChatWidget**: Chat interface
- **SettingsWidget**: Application settings

### Controllers
- **MainController**: Coordinates between UI and services

### Services
- **ConfigService**: Configuration and settings management
- **APIService**: Google Gemini API communication
- **RAGService**: Retrieval-Augmented Generation system

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Custom-Gemini-Agent-GUI
   ```

2. **Set up development environment**:
   ```bash
   python setup_dev.py
   ```

3. **Manual setup** (if setup script fails):
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode
```bash
python run.py
```

### Direct Execution
```bash
python app/main.py
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_config_service.py -v
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

## Code Quality

### Formatting
```bash
black app/ tests/
```

### Linting
```bash
flake8 app/ tests/
```

### Type Checking
```bash
mypy app/
```

## Building for Distribution

### Create Executable
```bash
python build.py
```

This creates:
- `dist/CustomGeminiAgentGUI.exe` - Standalone executable
- `CustomGeminiAgentGUI-Setup.exe` - Windows installer (if NSIS is available)

## Key Technologies

### Core Framework
- **PyQt6**: Desktop GUI framework
- **Python 3.8+**: Programming language

### AI/ML Stack
- **Google Gemini API**: Large language model
- **sentence-transformers**: Text embeddings
- **ChromaDB**: Vector database
- **langchain**: Document processing

### Additional Libraries
- **keyring**: Secure credential storage
- **loguru**: Logging
- **pydantic**: Data validation
- **watchdog**: File system monitoring
- **GitPython**: Git repository handling

## Configuration Management

### Application Data Location
- **Windows**: `%USERPROFILE%\.gemini_agent_gui\`
- **Linux/Mac**: `~/.gemini_agent_gui/`

### Directory Structure
```
.gemini_agent_gui/
├── config/
│   └── settings.json
├── gems/
│   └── *.json (saved configurations)
├── chroma_db/
│   └── (vector database files)
├── logs/
│   └── app.log
└── temp/
    └── (temporary files)
```

## API Integration

### Google Gemini API
- API key stored securely using system keyring
- Model: `gemini-pro`
- Safety settings configured for content filtering

### RAG System
- Embedding model: `msmarco-MiniLM-L-6-v3`
- Chunk size: 1000 characters (configurable)
- Chunk overlap: 200 characters (configurable)

## Adding New Features

### 1. Create Model (if needed)
```python
# app/models/new_model.py
from pydantic import BaseModel

class NewModel(BaseModel):
    # Define your model
    pass
```

### 2. Create Service (if needed)
```python
# app/services/new_service.py
class NewService:
    def __init__(self, config_service):
        self.config_service = config_service
```

### 3. Create Widget (if needed)
```python
# app/widgets/new_widget.py
from PyQt6.QtWidgets import QWidget

class NewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
```

### 4. Update Controller
```python
# app/controllers/main_controller.py
# Add new functionality to MainController
```

### 5. Add Tests
```python
# tests/test_new_feature.py
import pytest

def test_new_feature():
    # Write your tests
    pass
```

## Debugging

### Enable Debug Logging
Set environment variable:
```bash
export GEMINI_GUI_LOG_LEVEL=DEBUG
```

### Log Files
- Location: `~/.gemini_agent_gui/logs/app.log`
- Rotation: 10 MB files, 30 days retention

### Common Issues
1. **API Key Issues**: Check Windows Credential Manager
2. **Import Errors**: Verify all dependencies are installed
3. **UI Issues**: Check PyQt6 installation and version

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run quality checks: `black`, `flake8`, `mypy`, `pytest`
5. Commit changes: `git commit -am "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Create Pull Request

## Release Process

1. Update version numbers in relevant files
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test executable
5. Create release tag
6. Upload release artifacts
