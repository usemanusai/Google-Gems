"""
Session Service

Manages session state, window state, and user preferences.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from models.workspace import SessionState
from services.config_service import ConfigService


class SessionService:
    """Service for managing session state and user preferences."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.sessions_dir = config_service.get_app_directory() / "sessions"
        self.current_session_file = self.sessions_dir / "current_session.json"
        
        # Create directories
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Current session state
        self.current_session: Optional[SessionState] = None
        
        # Load or create current session
        self._load_or_create_session()
    
    def _load_or_create_session(self):
        """Load existing session or create a new one."""
        try:
            if self.current_session_file.exists():
                with open(self.current_session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.current_session = SessionState(**data)
                self.current_session.update_activity()
                logger.info("Loaded existing session")
            else:
                self.current_session = SessionState()
                self._save_current_session()
                logger.info("Created new session")
                
        except Exception as e:
            logger.error(f"Failed to load session, creating new one: {e}")
            self.current_session = SessionState()
            self._save_current_session()
    
    def _save_current_session(self):
        """Save the current session to file."""
        try:
            if self.current_session:
                with open(self.current_session_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_session.model_dump(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def set_current_workspace(self, workspace_id: str):
        """Set the current workspace."""
        if self.current_session:
            self.current_session.current_workspace_id = workspace_id
            self.current_session.update_activity()
            self._save_current_session()
            logger.debug(f"Set current workspace: {workspace_id}")
    
    def set_current_configuration(self, config_id: str):
        """Set the current configuration."""
        if self.current_session:
            self.current_session.current_configuration_id = config_id
            self.current_session.add_recent_configuration(config_id)
            self.current_session.update_activity()
            self._save_current_session()
            logger.debug(f"Set current configuration: {config_id}")
    
    def get_current_workspace_id(self) -> Optional[str]:
        """Get the current workspace ID."""
        return self.current_session.current_workspace_id if self.current_session else None
    
    def get_current_configuration_id(self) -> Optional[str]:
        """Get the current configuration ID."""
        return self.current_session.current_configuration_id if self.current_session else None
    
    def get_recent_configurations(self) -> List[str]:
        """Get recent configuration IDs."""
        return self.current_session.recent_configurations if self.current_session else []
    
    def save_window_geometry(self, geometry: Dict[str, int]):
        """Save window geometry."""
        if self.current_session:
            self.current_session.window_geometry = geometry
            self.current_session.update_activity()
            self._save_current_session()
            logger.debug("Saved window geometry")
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get saved window geometry."""
        if self.current_session and self.current_session.window_geometry:
            return self.current_session.window_geometry
        else:
            # Return default geometry
            return {
                "x": 100,
                "y": 100,
                "width": 1200,
                "height": 800
            }
    
    def save_panel_state(self, panel_name: str, is_visible: bool):
        """Save panel visibility state."""
        if self.current_session:
            self.current_session.panel_states[panel_name] = is_visible
            self.current_session.update_activity()
            self._save_current_session()
            logger.debug(f"Saved panel state: {panel_name} = {is_visible}")
    
    def get_panel_state(self, panel_name: str, default: bool = True) -> bool:
        """Get panel visibility state."""
        if self.current_session and panel_name in self.current_session.panel_states:
            return self.current_session.panel_states[panel_name]
        return default
    
    def save_chat_history(self, chat_history: List[Dict[str, Any]]):
        """Save chat history to session."""
        if self.current_session:
            # Keep only recent messages to avoid huge session files
            max_messages = 100
            if len(chat_history) > max_messages:
                chat_history = chat_history[-max_messages:]
            
            self.current_session.chat_history = chat_history
            self.current_session.update_activity()
            self._save_current_session()
            logger.debug(f"Saved chat history: {len(chat_history)} messages")
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get saved chat history."""
        return self.current_session.chat_history if self.current_session else []
    
    def clear_chat_history(self):
        """Clear chat history."""
        if self.current_session:
            self.current_session.chat_history = []
            self.current_session.update_activity()
            self._save_current_session()
            logger.debug("Cleared chat history")
    
    def create_session_backup(self, name: str) -> bool:
        """Create a named backup of the current session."""
        try:
            if not self.current_session:
                return False
            
            backup_file = self.sessions_dir / f"backup_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Created session backup: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session backup: {e}")
            return False
    
    def restore_session_backup(self, backup_file: str) -> bool:
        """Restore session from a backup file."""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.current_session = SessionState(**data)
            self.current_session.update_activity()
            self._save_current_session()
            
            logger.info(f"Restored session from backup: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore session backup: {e}")
            return False
    
    def list_session_backups(self) -> List[Dict[str, Any]]:
        """List available session backups."""
        try:
            backups = []
            
            for backup_file in self.sessions_dir.glob("backup_*.json"):
                try:
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime)
                    })
                except Exception as e:
                    logger.error(f"Error reading backup file {backup_file}: {e}")
                    continue
            
            # Sort by creation time, newest first
            backups.sort(key=lambda x: x["created"], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list session backups: {e}")
            return []
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old session files."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_count = 0
            
            for session_file in self.sessions_dir.glob("backup_*.json"):
                try:
                    stat = session_file.stat()
                    if datetime.fromtimestamp(stat.st_ctime) < cutoff_date:
                        session_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.error(f"Error cleaning session file {session_file}: {e}")
                    continue
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old session files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            if not self.current_session:
                return {}
            
            # Calculate session duration
            session_duration = datetime.now() - self.current_session.created_at
            
            # Count backups
            backup_count = len(list(self.sessions_dir.glob("backup_*.json")))
            
            return {
                "session_id": self.current_session.session_id,
                "created_at": self.current_session.created_at,
                "last_active_at": self.current_session.last_active_at,
                "session_duration": str(session_duration),
                "recent_configurations_count": len(self.current_session.recent_configurations),
                "chat_messages_count": len(self.current_session.chat_history),
                "backup_count": backup_count,
                "current_workspace": self.current_session.current_workspace_id,
                "current_configuration": self.current_session.current_configuration_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {}
    
    def reset_session(self):
        """Reset the current session to defaults."""
        try:
            # Keep some important state
            current_workspace = self.current_session.current_workspace_id if self.current_session else None
            
            # Create new session
            self.current_session = SessionState()
            
            # Restore workspace if it was set
            if current_workspace:
                self.current_session.current_workspace_id = current_workspace
            
            self._save_current_session()
            logger.info("Reset session to defaults")
            
        except Exception as e:
            logger.error(f"Failed to reset session: {e}")
    
    def export_session(self, export_path: str) -> bool:
        """Export current session to a file."""
        try:
            if not self.current_session:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_session.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Exported session to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return False
