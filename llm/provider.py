# file: llm/provider.py
from abc import ABC, abstractmethod
import json
import httpx
from typing import Dict, Any, Optional, List, Union

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text from the LLM"""
        pass
    
    @abstractmethod
    async def generate_structured(
        self, 
        prompt: str, 
        output_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate structured data from the LLM"""
        pass

class OllamaProvider(LLMProvider):
    """Implementation for ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b-instruct"):
        self.base_url = base_url
        self.model = model
        
    async def generate(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text from ollama"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "system": system_message if system_message else "",
                "options": {}
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
                
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()["response"]
    
    async def generate_structured(
        self, 
        prompt: str, 
        output_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate structured JSON data from ollama"""
        # Format the prompt to include the schema requirements
        formatted_prompt = f"""
        {prompt}
        
        You must respond ONLY with a valid JSON object matching this schema:
        {json.dumps(output_schema, indent=2)}
        
        Response:
        """
        
        # Add JSON format guidance to system message
        if system_message:
            enhanced_system = f"{system_message}\nYou must respond with valid JSON only, no other text."
        else:
            enhanced_system = "You must respond with valid JSON only, no other text."
        
        # Generate with low temperature for more consistent JSON
        response_text = await self.generate(
            formatted_prompt, 
            system_message=enhanced_system,
            temperature=temperature
        )
        
        # Extract and parse JSON from response
        try:
            # Find JSON object in response (in case model adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON object found in response")
        except json.JSONDecodeError:
            # Handle malformed JSON with retries or fall back to more structured approach
            # For now, return an error object
            return {"error": "Failed to parse JSON from LLM response", "raw_response": response_text}

# Factory class to get the appropriate provider
class LLMProviderFactory:
    @staticmethod
    def get_provider(provider_type: str, **kwargs) -> LLMProvider:
        if provider_type.lower() == "ollama":
            return OllamaProvider(**kwargs)
        # Add other providers as needed
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")