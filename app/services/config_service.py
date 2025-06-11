"""
Configuration Service

Handles all application configuration including settings persistence,
API key management, and session state.
"""

import json
import keyring
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class GemConfiguration(BaseModel):
    """Model for a Gem configuration."""
    name: str
    instructions: str = ""
    knowledge_sources: list[str] = Field(default_factory=list)
    created_at: str = ""
    modified_at: str = ""


class AppSettings(BaseSettings):
    """Application settings model."""
    window_geometry: Dict[str, int] = Field(default_factory=dict)
    last_gem_config: str = ""
    auto_save_interval: int = 300  # seconds
    max_chat_history: int = 1000
    embedding_model: str = "msmarco-MiniLM-L-6-v3"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_prefix = "GEMINI_GUI_"


class ConfigService:
    """Service for managing application configuration."""
    
    SERVICE_NAME = "CustomGeminiAgentGUI"
    API_KEY_NAME = "google_gemini_api_key"
    
    def __init__(self):
        self.app_dir = Path.home() / ".gemini_agent_gui"
        self.config_dir = self.app_dir / "config"
        self.gems_dir = self.app_dir / "gems"
        self.settings_file = self.config_dir / "settings.json"
        
        # Create directories
        self.app_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        self.gems_dir.mkdir(exist_ok=True)
        
        # Load settings
        self.settings = self.load_settings()
        
        logger.info(f"ConfigService initialized with app dir: {self.app_dir}")
    
    def load_settings(self) -> AppSettings:
        """Load application settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AppSettings(**data)
            else:
                logger.info("Settings file not found, using defaults")
                return AppSettings()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return AppSettings()
    
    def save_settings(self) -> bool:
        """Save application settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.model_dump(), f, indent=2)
            logger.debug("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def get_api_key(self) -> Optional[str]:
        """Get the Google Gemini API key from secure storage."""
        try:
            api_key = keyring.get_password(self.SERVICE_NAME, self.API_KEY_NAME)
            if api_key:
                logger.debug("API key retrieved from secure storage")
            else:
                logger.warning("No API key found in secure storage")
            return api_key
        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            return None
    
    def set_api_key(self, api_key: str) -> bool:
        """Store the Google Gemini API key in secure storage."""
        try:
            keyring.set_password(self.SERVICE_NAME, self.API_KEY_NAME, api_key)
            logger.info("API key stored in secure storage")
            return True
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            return False
    
    def delete_api_key(self) -> bool:
        """Delete the API key from secure storage."""
        try:
            keyring.delete_password(self.SERVICE_NAME, self.API_KEY_NAME)
            logger.info("API key deleted from secure storage")
            return True
        except Exception as e:
            logger.error(f"Failed to delete API key: {e}")
            return False
    
    def save_gem_configuration(self, gem_config: GemConfiguration) -> bool:
        """Save a gem configuration to file."""
        try:
            gem_file = self.gems_dir / f"{gem_config.name}.json"
            with open(gem_file, 'w', encoding='utf-8') as f:
                json.dump(gem_config.model_dump(), f, indent=2)
            logger.info(f"Gem configuration '{gem_config.name}' saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save gem configuration: {e}")
            return False
    
    def load_gem_configuration(self, name: str) -> Optional[GemConfiguration]:
        """Load a gem configuration from file."""
        try:
            gem_file = self.gems_dir / f"{name}.json"
            if gem_file.exists():
                with open(gem_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return GemConfiguration(**data)
            else:
                logger.warning(f"Gem configuration '{name}' not found")
                return None
        except Exception as e:
            logger.error(f"Failed to load gem configuration '{name}': {e}")
            return None
    
    def list_gem_configurations(self) -> list[str]:
        """List all available gem configurations."""
        try:
            gem_files = list(self.gems_dir.glob("*.json"))
            return [f.stem for f in gem_files]
        except Exception as e:
            logger.error(f"Failed to list gem configurations: {e}")
            return []
    
    def delete_gem_configuration(self, name: str) -> bool:
        """Delete a gem configuration."""
        try:
            gem_file = self.gems_dir / f"{name}.json"
            if gem_file.exists():
                gem_file.unlink()
                logger.info(f"Gem configuration '{name}' deleted")
                return True
            else:
                logger.warning(f"Gem configuration '{name}' not found")
                return False
        except Exception as e:
            logger.error(f"Failed to delete gem configuration '{name}': {e}")
            return False
    
    def get_app_directory(self) -> Path:
        """Get the application directory path."""
        return self.app_dir
    
    def get_config_directory(self) -> Path:
        """Get the configuration directory path."""
        return self.config_dir
    
    def get_gems_directory(self) -> Path:
        """Get the gems directory path."""
        return self.gems_dir
