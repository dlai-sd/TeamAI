"""
LLMProcessor Component
Interfaces with Groq API for text processing
"""
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from groq import Groq

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from components.base import BaseComponent


class LLMProcessor(BaseComponent):
    """Process text with LLM (Groq API)"""
    
    # Model pricing (per 1M tokens)
    PRICING = {
        'llama-3.1-8b-instant': {'input': 0.05, 'output': 0.08},
        'llama-3.3-70b-versatile': {'input': 0.59, 'output': 0.79}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, mock_mode: bool = False):
        super().__init__(config, mock_mode)
        self.model = self.config.get('model', 'llama-3.1-8b-instant')
        self.fallback_model = self.config.get('fallback_model', 'llama-3.3-70b-versatile')
        self.temperature = self.config.get('temperature', 0.2)
        self.max_tokens = self.config.get('max_tokens', 2048)
        self.api_key = self.config.get('api_key') or os.getenv('GROQ_API_KEY')
        
        if not self.mock_mode and self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
    
    def validate_config(self) -> bool:
        """Validate LLM configuration"""
        if not self.mock_mode and not self.api_key:
            return False
        if self.temperature < 0 or self.temperature > 2:
            return False
        if self.max_tokens < 1:
            return False
        return True
    
    async def execute(self, prompt: str, system_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Process text with LLM
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            Dict with response and metadata
        """
        if self.mock_mode:
            return self._mock_process(prompt)
        
        if not self.validate_config():
            raise ValueError("Invalid LLM configuration - missing API key")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Try primary model
        try:
            response = await self._call_groq(messages, self.model)
            return response
        except Exception as e:
            print(f"Primary model {self.model} failed: {str(e)}")
            
            # Fallback to larger model
            try:
                print(f"Falling back to {self.fallback_model}")
                response = await self._call_groq(messages, self.fallback_model)
                response['fallback_used'] = True
                return response
            except Exception as fallback_error:
                raise Exception(f"Both models failed. Primary: {str(e)}, Fallback: {str(fallback_error)}")
    
    async def _call_groq(self, messages: List[Dict], model: str) -> Dict[str, Any]:
        """Call Groq API"""
        import asyncio
        
        # Groq client is sync, so we run it in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        )
        
        # Calculate cost
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        return {
            'content': response.choices[0].message.content,
            'model': model,
            'usage': {
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'cost': cost,
            'fallback_used': False
        }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost in USD"""
        pricing = self.PRICING.get(model, self.PRICING['llama-3.1-8b-instant'])
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        return round(input_cost + output_cost, 6)
    
    def _mock_process(self, prompt: str) -> Dict[str, Any]:
        """Return mock data for testing"""
        return {
            'content': f"Mock LLM response for: {prompt[:50]}...\n\nThis is a simulated analysis with detailed insights.",
            'model': self.model,
            'usage': {
                'input_tokens': 100,
                'output_tokens': 50,
                'total_tokens': 150
            },
            'cost': 0.000015,
            'fallback_used': False
        }
