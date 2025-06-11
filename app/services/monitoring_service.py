"""
Monitoring Service

Handles real-time file system monitoring for automatic knowledge base updates.
"""

import time
from pathlib import Path
from typing import Dict, Set, Callable, Optional
from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    logger.warning("watchdog not available, file monitoring disabled")
    WATCHDOG_AVAILABLE = False

from models.knowledge_source import KnowledgeSource, SourceType, SourceStatus


class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, callback: Callable[[str, str], None]):
        super().__init__()
        self.callback = callback
        self.supported_extensions = {
            '.txt', '.md', '.pdf', '.docx', '.doc', '.py', '.js', 
            '.html', '.css', '.json', '.xml', '.csv', '.rst'
        }
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_extensions:
                logger.debug(f"File modified: {file_path}")
                self.callback(str(file_path), "modified")
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_extensions:
                logger.debug(f"File created: {file_path}")
                self.callback(str(file_path), "created")
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.supported_extensions:
                logger.debug(f"File deleted: {file_path}")
                self.callback(str(file_path), "deleted")


class MonitoringService(QThread):
    """Service for monitoring file system changes."""
    
    # Signals
    file_changed = pyqtSignal(str, str, str)  # source_id, file_path, event_type
    monitoring_error = pyqtSignal(str, str)   # source_id, error_message
    
    def __init__(self):
        super().__init__()
        self.observer = None
        self.monitored_sources: Dict[str, Dict] = {}
        self.is_monitoring = False
        
        if WATCHDOG_AVAILABLE:
            self.observer = Observer()
        else:
            logger.warning("File monitoring not available (watchdog not installed)")
    
    def start_monitoring(self):
        """Start the file monitoring service."""
        if not WATCHDOG_AVAILABLE:
            logger.warning("Cannot start monitoring: watchdog not available")
            return False
        
        try:
            if not self.is_monitoring:
                self.observer.start()
                self.is_monitoring = True
                logger.info("File monitoring service started")
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to start monitoring service: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop the file monitoring service."""
        if not WATCHDOG_AVAILABLE:
            return
        
        try:
            if self.is_monitoring and self.observer:
                self.observer.stop()
                self.observer.join()
                self.is_monitoring = False
                logger.info("File monitoring service stopped")
        except Exception as e:
            logger.error(f"Failed to stop monitoring service: {e}")
    
    def add_source_monitoring(self, source: KnowledgeSource) -> bool:
        """Add a knowledge source for monitoring."""
        if not WATCHDOG_AVAILABLE:
            logger.warning("Cannot monitor source: watchdog not available")
            return False
        
        if source.source_type not in [SourceType.FILE, SourceType.FOLDER]:
            logger.debug(f"Source type {source.source_type} not supported for monitoring")
            return False
        
        try:
            path = Path(source.path)
            if not path.exists():
                logger.warning(f"Path does not exist for monitoring: {source.path}")
                return False
            
            # Create handler for this source
            handler = FileChangeHandler(
                lambda file_path, event_type: self._on_file_change(source.id, file_path, event_type)
            )
            
            # Determine watch path
            if source.source_type == SourceType.FILE:
                watch_path = path.parent
                file_filter = path.name
            else:  # FOLDER
                watch_path = path
                file_filter = None
            
            # Add watch
            watch = self.observer.schedule(handler, str(watch_path), recursive=True)
            
            # Store monitoring info
            self.monitored_sources[source.id] = {
                "source": source,
                "handler": handler,
                "watch": watch,
                "path": str(watch_path),
                "file_filter": file_filter
            }
            
            # Update source status
            source.update_status(SourceStatus.MONITORING)
            
            logger.info(f"Started monitoring: {source.get_display_name()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add monitoring for {source.get_display_name()}: {e}")
            self.monitoring_error.emit(source.id, str(e))
            return False
    
    def remove_source_monitoring(self, source_id: str) -> bool:
        """Remove monitoring for a knowledge source."""
        if not WATCHDOG_AVAILABLE:
            return False
        
        try:
            if source_id in self.monitored_sources:
                monitor_info = self.monitored_sources[source_id]
                self.observer.unschedule(monitor_info["watch"])
                del self.monitored_sources[source_id]
                logger.info(f"Stopped monitoring source: {source_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove monitoring for {source_id}: {e}")
            return False
    
    def _on_file_change(self, source_id: str, file_path: str, event_type: str):
        """Handle file change events."""
        try:
            if source_id not in self.monitored_sources:
                return
            
            monitor_info = self.monitored_sources[source_id]
            source = monitor_info["source"]
            
            # Apply file filter if monitoring a single file
            if monitor_info["file_filter"]:
                if Path(file_path).name != monitor_info["file_filter"]:
                    return
            
            # Check if file is within the monitored path
            file_path_obj = Path(file_path)
            watch_path_obj = Path(monitor_info["path"])
            
            try:
                file_path_obj.relative_to(watch_path_obj)
            except ValueError:
                # File is not within monitored path
                return
            
            logger.info(f"File {event_type}: {file_path} (source: {source.get_display_name()})")
            
            # Emit signal for processing
            self.file_changed.emit(source_id, file_path, event_type)
            
        except Exception as e:
            logger.error(f"Error handling file change: {e}")
            self.monitoring_error.emit(source_id, str(e))
    
    def get_monitored_sources(self) -> Dict[str, Dict]:
        """Get information about currently monitored sources."""
        return {
            source_id: {
                "source_name": info["source"].get_display_name(),
                "path": info["path"],
                "file_filter": info["file_filter"]
            }
            for source_id, info in self.monitored_sources.items()
        }
    
    def is_source_monitored(self, source_id: str) -> bool:
        """Check if a source is currently being monitored."""
        return source_id in self.monitored_sources
    
    def run(self):
        """Run the monitoring service thread."""
        # This method is called when the thread starts
        # The actual monitoring is handled by the watchdog observer
        while self.is_monitoring:
            time.sleep(1)
    
    def __del__(self):
        """Cleanup when service is destroyed."""
        self.stop_monitoring()
