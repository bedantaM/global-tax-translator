"""
AI Processor Service
Handles communication with LLM APIs via LiteLLM
Supports: OpenAI, Azure, Anthropic, Google, and 100+ other providers
"""

import json
import logging
import os
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# LiteLLM supports multiple providers - set API keys via environment variables:
# - OPENAI_API_KEY for OpenAI models (gpt-4, gpt-3.5-turbo)
# - ANTHROPIC_API_KEY for Claude models (claude-3-opus, claude-3-sonnet)
# - AZURE_API_KEY, AZURE_API_BASE for Azure OpenAI
# - GEMINI_API_KEY for Google Gemini
# See: https://docs.litellm.ai/docs/providers


class AIProcessor:
    """Service for AI/LLM processing"""
    
    # Country code to name mapping
    COUNTRY_NAMES = {
        "US": "United States",
        "BR": "Brazil",
        "DE": "Germany",
        "FR": "France",
        "GB": "United Kingdom",
        "IT": "Italy",
        "ES": "Spain",
        "PT": "Portugal",
        "NL": "Netherlands",
        "BE": "Belgium",
        "AT": "Austria",
        "CH": "Switzerland",
        "PL": "Poland",
        "CZ": "Czech Republic",
        "SE": "Sweden",
        "NO": "Norway",
        "DK": "Denmark",
        "FI": "Finland",
        "IE": "Ireland",
        "AU": "Australia",
        "NZ": "New Zealand",
        "CA": "Canada",
        "MX": "Mexico",
        "AR": "Argentina",
        "CL": "Chile",
        "CO": "Colombia",
        "PE": "Peru",
        "JP": "Japan",
        "KR": "South Korea",
        "CN": "China",
        "IN": "India",
        "SG": "Singapore",
        "HK": "Hong Kong",
        "AE": "United Arab Emirates",
        "SA": "Saudi Arabia",
        "ZA": "South Africa",
        "NG": "Nigeria",
        "EG": "Egypt",
        "IL": "Israel",
        "TR": "Turkey",
        "RU": "Russia",
        "UA": "Ukraine",
    }
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI Processor with LiteLLM
        
        Args:
            api_key: API key (defaults to env var based on model provider)
            model: Model to use - LiteLLM format (defaults to env var or gpt-4-turbo-preview)
                   Examples:
                   - OpenAI: "gpt-4-turbo-preview", "gpt-4o", "gpt-3.5-turbo"
                   - Azure: "azure/gpt-4", "azure/gpt-4-turbo"
                   - Anthropic: "claude-3-opus-20240229", "claude-3-sonnet-20240229"
                   - Google: "gemini/gemini-pro"
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"))
        
        # Set the API key in environment for LiteLLM
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
        
        if not self.api_key:
            logger.warning("API key not set. AI processing will fail. Set OPENAI_API_KEY or provider-specific key.")
    
    def get_country_name(self, country_code: str) -> str:
        """Get full country name from code"""
        return self.COUNTRY_NAMES.get(country_code.upper(), country_code)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        Process a prompt with the LLM using LiteLLM
        
        Args:
            system_prompt: System/instruction prompt
            user_prompt: User message/query
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response text
        """
        try:
            from litellm import completion
            
            # Build completion kwargs
            completion_kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Add JSON response format for OpenAI models
            if self.model.startswith(("gpt-", "azure/")):
                completion_kwargs["response_format"] = {"type": "json_object"}
            
            response = completion(**completion_kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            raise
    
    async def process_with_json_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Process a prompt and return parsed JSON
        
        Args:
            system_prompt: System/instruction prompt
            user_prompt: User message/query
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Parsed JSON response
        """
        response_text = await self.process(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text}")
            
            # Try to extract JSON from the response
            cleaned = self._extract_json(response_text)
            if cleaned:
                return json.loads(cleaned)
            
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    def _extract_json(self, text: str) -> Optional[str]:
        """
        Try to extract JSON from text that might have extra content
        
        Args:
            text: Text that might contain JSON
            
        Returns:
            Extracted JSON string or None
        """
        import re
        
        # Try to find JSON object
        json_pattern = r'\{[\s\S]*\}'
        matches = re.findall(json_pattern, text)
        
        for match in matches:
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue
        
        return None
    
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except Exception:
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4
    
    async def chunk_text(self, text: str, max_tokens: int = 6000) -> list[str]:
        """
        Split text into chunks that fit within token limits
        
        Args:
            text: Input text
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            tokens = encoding.encode(text)
            
            chunks = []
            current_chunk = []
            current_count = 0
            
            for token in tokens:
                if current_count + 1 > max_tokens:
                    chunks.append(encoding.decode(current_chunk))
                    current_chunk = [token]
                    current_count = 1
                else:
                    current_chunk.append(token)
                    current_count += 1
            
            if current_chunk:
                chunks.append(encoding.decode(current_chunk))
            
            return chunks
            
        except Exception:
            # Fallback: simple character-based chunking
            char_limit = max_tokens * 4  # Rough estimate
            chunks = []
            
            for i in range(0, len(text), char_limit):
                chunks.append(text[i:i + char_limit])
            
            return chunks
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return bool(self.api_key)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on AI service using LiteLLM
        
        Returns:
            Health status dict
        """
        if not self.api_key:
            return {
                "status": "unavailable",
                "error": "API key not configured"
            }
        
        try:
            from litellm import completion
            
            # Simple test call
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "model": self.model,
                "provider": "litellm",
                "response_id": response.id if hasattr(response, 'id') else "ok"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class MockAIProcessor(AIProcessor):
    """
    Mock AI Processor for testing and demo purposes
    Returns realistic sample data without calling actual LLM
    """
    
    def __init__(self):
        super().__init__(api_key="mock-key", model="mock-model")
    
    async def process(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """Return mock response based on prompt type"""
        
        if "extract" in system_prompt.lower():
            return json.dumps(self._get_mock_extraction())
        elif "json config" in system_prompt.lower():
            return json.dumps(self._get_mock_json_config())
        elif "sql" in system_prompt.lower():
            return json.dumps(self._get_mock_sql_migration())
        elif "policy" in system_prompt.lower():
            return json.dumps(self._get_mock_policy())
        elif "code" in system_prompt.lower():
            return json.dumps(self._get_mock_code())
        else:
            return json.dumps({"message": "Mock response"})
    
    def _get_mock_extraction(self) -> dict:
        return {
            "summary": "Sample tax document with VAT rates and filing deadlines",
            "tax_types": ["VAT"],
            "rates": [
                {
                    "name": "standard",
                    "rate": 0.19,
                    "description": "Standard VAT rate",
                    "conditions": ["goods", "services"],
                    "exemptions": ["healthcare", "education"]
                }
            ],
            "brackets": [],
            "thresholds": [
                {
                    "name": "registration_threshold",
                    "amount": 10000,
                    "currency": "EUR",
                    "description": "VAT registration threshold"
                }
            ],
            "deadlines": [
                {
                    "name": "vat_return",
                    "deadline_type": "filing",
                    "frequency": "quarterly",
                    "day_of_period": 15,
                    "description": "Quarterly VAT return"
                }
            ],
            "rules": [],
            "confidence_score": 0.85,
            "warnings": ["Mock data - for demonstration only"]
        }
    
    def _get_mock_json_config(self) -> dict:
        return {
            "version": "1.0",
            "country": "DE",
            "country_name": "Germany",
            "tax_type": "VAT",
            "rules": [
                {
                    "rule_id": "vat_standard",
                    "name": "Standard VAT Rate",
                    "type": "rate",
                    "value": 0.19
                }
            ]
        }
    
    def _get_mock_sql_migration(self) -> dict:
        return {
            "migration_name": "add_de_vat_rates_20240101",
            "description": "Add German VAT rates",
            "tables_affected": ["tax_rates"],
            "up_script": "INSERT INTO tax_rates (country_code, rate) VALUES ('DE', 0.19);",
            "down_script": "DELETE FROM tax_rates WHERE country_code = 'DE';"
        }
    
    def _get_mock_policy(self) -> dict:
        return {
            "policy_name": "germany_vat_policy",
            "version": "1.0",
            "description": "German VAT policy",
            "rules": []
        }
    
    def _get_mock_code(self) -> dict:
        return {
            "filename": "tax_calculator_de.py",
            "description": "German tax calculator",
            "dependencies": [],
            "code": "# Mock code\nclass TaxCalculator:\n    pass"
        }
    
    def is_available(self) -> bool:
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "model": "mock"}
