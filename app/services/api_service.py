"""
API Service

Handles all communication with external APIs, primarily Google Gemini API.
"""

import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from loguru import logger

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai not available, using mock responses")
    GENAI_AVAILABLE = False

from services.config_service import ConfigService


class APIService:
    """Service for managing API communications."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.model = None
        self.is_configured = False
        
    def configure_api(self) -> bool:
        """Configure the Google Gemini API."""
        try:
            if not GENAI_AVAILABLE:
                logger.warning("Google Generative AI library not available")
                return False

            api_key = self.config_service.get_api_key()
            if not api_key:
                logger.warning("No API key found")
                return False

            # Configure the API
            genai.configure(api_key=api_key)

            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )

            self.is_configured = True
            logger.info("Google Gemini API configured successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to configure API: {e}")
            self.is_configured = False
            return False
    
    async def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            if not self.is_configured:
                if not self.configure_api():
                    return False
            
            # Send a simple test message
            response = await self.generate_response("Hello, this is a test message.")
            return response is not None
            
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """Generate a response using the Gemini API."""
        try:
            if not GENAI_AVAILABLE:
                # Return a mock response for testing
                await asyncio.sleep(1)  # Simulate API delay
                return f"Mock response to: {prompt[:50]}... (Google Generative AI library not available)"

            if not self.is_configured:
                if not self.configure_api():
                    raise Exception("API not configured")

            # Build the full prompt
            full_prompt = self._build_prompt(prompt, context, chat_history)

            # Generate response
            response = self.model.generate_content(full_prompt)

            if response.text:
                logger.debug(f"Generated response: {response.text[:100]}...")
                return response.text
            else:
                logger.warning("Empty response from API")
                return None

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return None
    
    async def generate_response_stream(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using the Gemini API."""
        try:
            if not self.is_configured:
                if not self.configure_api():
                    raise Exception("API not configured")
            
            # Build the full prompt
            full_prompt = self._build_prompt(prompt, context, chat_history)
            
            # Generate streaming response
            response = self.model.generate_content(full_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"Error: {str(e)}"
    
    def _build_prompt(
        self, 
        user_prompt: str, 
        context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build the complete prompt for the API."""
        parts = []
        
        # Add chat history if provided
        if chat_history:
            for entry in chat_history[-10:]:  # Last 10 messages
                role = entry.get("role", "")
                content = entry.get("content", "")
                if role == "user":
                    parts.append(f"User: {content}")
                elif role == "assistant":
                    parts.append(f"Assistant: {content}")
        
        # Add context from RAG if provided
        if context:
            parts.append(f"Context from knowledge base:\n{context}")
        
        # Add current user prompt
        parts.append(f"User: {user_prompt}")
        
        return "\n\n".join(parts)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.is_configured:
            return {"configured": False}
        
        return {
            "configured": True,
            "model_name": "gemini-pro",
            "api_configured": self.is_configured
        }
