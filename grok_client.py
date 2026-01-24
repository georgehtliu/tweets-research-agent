"""
Grok API Client
Handles all interactions with Grok API
"""
import os
import json
from typing import Dict, Optional, List
from openai import OpenAI
import config

class GrokClient:
    """Client for interacting with Grok API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Grok client
        
        Args:
            api_key: Grok API key (if None, uses config)
        """
        self.api_key = api_key or config.GROK_API_KEY
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY not found. Set it in .env file or pass as argument.")
        
        # Initialize OpenAI-compatible client for xAI
        # Note: xAI uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=config.GROK_BASE_URL
        )
    
    def call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
        response_format: Optional[Dict] = None
    ) -> Dict:
        """
        Call Grok API
        
        Args:
            model: Model name (e.g., "grok-beta")
            messages: List of message dicts with "role" and "content"
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            response_format: Optional response format (e.g., {"type": "json_object"})
            
        Returns:
            Dictionary with "content", "tokens_used", "model"
        """
        # Prepare messages
        api_messages = []
        
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        
        api_messages.extend(messages)
        
        # Prepare parameters
        params = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens or config.MAX_TOKENS_RESPONSE,
            "temperature": temperature or config.TEMPERATURE
        }
        
        if response_format:
            params["response_format"] = response_format
        
        try:
            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            
            # Estimate tokens (rough approximation)
            input_tokens = sum(len(msg.get("content", "")) // 4 for msg in api_messages)
            output_tokens = len(content) // 4
            
            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": model,
                "success": True
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Grok API Error: {error_msg}")
            
            # Provide helpful error messages
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                error_msg += "\n💡 Tip: Check your GROK_API_KEY in .env file"
            elif "rate limit" in error_msg.lower():
                error_msg += "\n💡 Tip: You've hit rate limits. Wait a moment and try again."
            elif "model" in error_msg.lower():
                error_msg += f"\n💡 Tip: Check if model '{model}' is available in your API plan"
            
            return {
                "content": f"[Error: {error_msg}]",
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "model": model,
                "success": False,
                "error": error_msg
            }
    
    def parse_json_response(self, content: str) -> Dict:
        """Parse JSON from response, handling markdown code blocks"""
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON object
            try:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
            except:
                pass
            
            # Return as fallback
            return {"raw_response": content}
