"""
Google Drive Service

Handles Google Drive integration for knowledge source ingestion.
"""

import io
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    logger.warning("Google API libraries not available")
    GOOGLE_API_AVAILABLE = False

from services.config_service import ConfigService


class GoogleDriveService:
    """Service for Google Drive integration."""
    
    # Google Drive API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Supported file types for download
    DOWNLOADABLE_TYPES = {
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.google-apps.spreadsheet': 'text/csv',
        'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain': 'text/plain',
        'application/pdf': 'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': None,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': None,
        'text/csv': None,
        'application/json': None,
        'text/markdown': None,
        'text/x-python': None,
        'text/javascript': None,
        'text/html': None,
        'text/css': None,
    }
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.service = None
        self.credentials = None
        
        if not GOOGLE_API_AVAILABLE:
            logger.warning("Google Drive service not available (missing dependencies)")
    
    def authenticate(self, credentials_file: Optional[str] = None) -> bool:
        """Authenticate with Google Drive API."""
        if not GOOGLE_API_AVAILABLE:
            logger.error("Google API libraries not available")
            return False
        
        try:
            creds = None
            token_file = self.config_service.get_config_directory() / "google_drive_token.json"
            
            # Load existing credentials
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not credentials_file:
                        credentials_file = self.config_service.get_config_directory() / "google_drive_credentials.json"
                    
                    if not Path(credentials_file).exists():
                        logger.error(f"Google Drive credentials file not found: {credentials_file}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('drive', 'v3', credentials=creds)
            
            logger.info("Google Drive authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            return False
    
    def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in Google Drive."""
        if not self.service:
            logger.error("Google Drive service not authenticated")
            return []
        
        try:
            # Build query
            search_query = []
            
            if folder_id:
                search_query.append(f"'{folder_id}' in parents")
            
            if query:
                search_query.append(query)
            
            # Add filter for supported file types
            mime_types = list(self.DOWNLOADABLE_TYPES.keys())
            mime_query = " or ".join([f"mimeType='{mime}'" for mime in mime_types])
            search_query.append(f"({mime_query})")
            
            final_query = " and ".join(search_query) if search_query else None
            
            # Execute search
            results = self.service.files().list(
                q=final_query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in Google Drive")
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list Google Drive files: {e}")
            return []
    
    def download_file(self, file_id: str, file_name: str, mime_type: str) -> Optional[Dict[str, Any]]:
        """Download a file from Google Drive."""
        if not self.service:
            logger.error("Google Drive service not authenticated")
            return None
        
        try:
            # Determine export format for Google Docs
            export_mime_type = self.DOWNLOADABLE_TYPES.get(mime_type)
            
            if export_mime_type:
                # Export Google Docs format
                request = self.service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            else:
                # Download regular file
                request = self.service.files().get_media(fileId=file_id)
            
            # Download content
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Get file content
            content = file_io.getvalue()
            
            # Determine file extension
            if export_mime_type:
                if export_mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    extension = '.docx'
                elif export_mime_type == 'text/csv':
                    extension = '.csv'
                elif export_mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                    extension = '.pptx'
                else:
                    extension = '.txt'
            else:
                # Use original file extension or determine from mime type
                if '.' in file_name:
                    extension = Path(file_name).suffix
                else:
                    extension = self._get_extension_from_mime_type(mime_type)
            
            return {
                "content": content,
                "filename": file_name,
                "extension": extension,
                "mime_type": mime_type,
                "size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            return None
    
    def _get_extension_from_mime_type(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_to_ext = {
            'text/plain': '.txt',
            'application/pdf': '.pdf',
            'text/markdown': '.md',
            'text/x-python': '.py',
            'text/javascript': '.js',
            'text/html': '.html',
            'text/css': '.css',
            'application/json': '.json',
        }
        return mime_to_ext.get(mime_type, '.txt')
    
    def get_folder_info(self, folder_url: str) -> Optional[Dict[str, Any]]:
        """Extract folder information from Google Drive URL."""
        try:
            # Extract folder ID from URL
            if '/folders/' in folder_url:
                folder_id = folder_url.split('/folders/')[1].split('?')[0].split('/')[0]
            elif 'id=' in folder_url:
                folder_id = folder_url.split('id=')[1].split('&')[0]
            else:
                logger.error(f"Invalid Google Drive folder URL: {folder_url}")
                return None
            
            if not self.service:
                logger.error("Google Drive service not authenticated")
                return None
            
            # Get folder metadata
            folder_info = self.service.files().get(
                fileId=folder_id,
                fields="id, name, mimeType"
            ).execute()
            
            if folder_info.get('mimeType') != 'application/vnd.google-apps.folder':
                logger.error(f"URL does not point to a folder: {folder_url}")
                return None
            
            return {
                "id": folder_id,
                "name": folder_info.get('name', 'Unknown Folder'),
                "url": folder_url
            }
            
        except Exception as e:
            logger.error(f"Failed to get folder info: {e}")
            return None
    
    def process_folder(self, folder_url: str) -> List[Dict[str, Any]]:
        """Process all files in a Google Drive folder."""
        documents = []
        
        try:
            # Get folder info
            folder_info = self.get_folder_info(folder_url)
            if not folder_info:
                return documents
            
            folder_id = folder_info["id"]
            folder_name = folder_info["name"]
            
            # List all files in folder
            files = self.list_files(folder_id=folder_id)
            
            logger.info(f"Processing {len(files)} files from Google Drive folder: {folder_name}")
            
            for file_info in files:
                try:
                    # Download file content
                    file_data = self.download_file(
                        file_info['id'],
                        file_info['name'],
                        file_info['mimeType']
                    )
                    
                    if file_data:
                        # Convert to text if needed
                        content = self._extract_text_content(file_data)
                        
                        if content:
                            documents.append({
                                "content": content,
                                "metadata": {
                                    "source": folder_url,
                                    "filename": file_data["filename"],
                                    "file_type": file_data["extension"],
                                    "file_size": file_data["size"],
                                    "mime_type": file_data["mime_type"],
                                    "folder_name": folder_name,
                                    "drive_file_id": file_info['id']
                                }
                            })
                            
                except Exception as e:
                    logger.error(f"Failed to process file {file_info['name']}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(documents)} documents from Google Drive")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to process Google Drive folder: {e}")
            return documents
    
    def _extract_text_content(self, file_data: Dict[str, Any]) -> Optional[str]:
        """Extract text content from downloaded file data."""
        try:
            content = file_data["content"]
            extension = file_data["extension"].lower()
            
            if extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.csv']:
                # Text files - decode directly
                return content.decode('utf-8', errors='ignore')
            
            elif extension == '.docx':
                # Word documents - would need python-docx
                try:
                    import docx
                    from io import BytesIO
                    
                    doc = docx.Document(BytesIO(content))
                    text_content = []
                    for paragraph in doc.paragraphs:
                        text_content.append(paragraph.text)
                    return '\n'.join(text_content)
                except ImportError:
                    logger.warning("python-docx not available for .docx files")
                    return None
            
            elif extension == '.pdf':
                # PDF files - would need PyPDF2 or similar
                try:
                    import PyPDF2
                    from io import BytesIO
                    
                    pdf_reader = PyPDF2.PdfReader(BytesIO(content))
                    text_content = []
                    for page in pdf_reader.pages:
                        text_content.append(page.extract_text())
                    return '\n'.join(text_content)
                except ImportError:
                    logger.warning("PyPDF2 not available for .pdf files")
                    return None
            
            else:
                # Try to decode as text
                try:
                    return content.decode('utf-8', errors='ignore')
                except:
                    logger.warning(f"Cannot extract text from file type: {extension}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to extract text content: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if Google Drive is authenticated."""
        return self.service is not None and self.credentials is not None
