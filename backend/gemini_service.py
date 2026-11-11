"""
Gemini Service Module for AgriVerse AI.
Integrates with the official Google GenAI Python SDK (`google-genai`).
Includes resilient fallback model cascade and structured error handling.
"""
import os
import logging
from config import Config

logger = logging.getLogger("AgriVerse.GeminiService")

class GeminiService:
    """Wrapper for Google Gen AI client operations."""
    
    # Priority cascade of models for high availability
    FALLBACK_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.8-flash",
        "gemini-2.5-flash-lite"
    ]
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.client = None
        self._init_client()
        
    def _init_client(self):
        """Initialize the official google-genai Client."""
        if not self.api_key or self.api_key.startswith("your_"):
            return
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Client initialization failed: {e}")

    def is_configured(self) -> bool:
        """Check if Gemini API client is ready."""
        return self.client is not None

    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate text response with automatic model fallback across supported models.
        """
        if not self.is_configured():
            return "Gemini API key is not configured. Please check your .env file."

        from google.genai import types

        # Build config with optional system instructions
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4
            )

        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        
        last_error = None
        for model in models_to_try:
            try:
                kwargs = {"model": model, "contents": prompt}
                if config:
                    kwargs["config"] = config
                    
                response = self.client.models.generate_content(**kwargs)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}. Trying fallback...")
                last_error = e
                continue
                
        raise RuntimeError(f"All Gemini models exhausted. Last error: {last_error}")
