"""
Output Generator Service
Generates JSON configs, SQL migrations, policy definitions, and code
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from models.schemas import (
    ExtractedEntities, JSONConfig, SQLMigration, 
    PolicyDefinition, GeneratedCode, TaxType
)
from prompts.templates import PromptTemplates
from services.ai_processor import AIProcessor

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Service for generating various output formats from extracted entities"""
    
    def __init__(self, ai_processor: AIProcessor):
        self.ai_processor = ai_processor
    
    async def generate_all(
        self, entities: ExtractedEntities, country: str, country_name: str
    ) -> Dict[str, Any]:
        """Generate all output formats"""
        results = {}
        results["json_config"] = await self.generate_json_config(entities, country, country_name)
        results["sql_migration"] = await self.generate_sql_migration(entities, country, country_name)
        results["policy_definition"] = await self.generate_policy_definition(entities, country, country_name)
        results["generated_code"] = await self.generate_code(entities, country, country_name)
        return results
    
    async def generate_json_config(
        self, entities: ExtractedEntities, country: str, country_name: str
    ) -> JSONConfig:
        """Generate JSON configuration"""
        entities_json = json.dumps(entities.model_dump(), default=str, indent=2)
        system_prompt, user_prompt = PromptTemplates.get_json_config_prompt(
            entities_json=entities_json, country=country, country_name=country_name
        )
        response = await self.ai_processor.process_with_json_response(
            system_prompt=system_prompt, user_prompt=user_prompt
        )
        return self._parse_json_config(response, country, country_name, entities)
    
    def _parse_json_config(
        self, response: Dict, country: str, country_name: str, entities: ExtractedEntities
    ) -> JSONConfig:
        """Parse AI response into JSONConfig"""
        tax_type = TaxType.VAT
        if entities.tax_types:
            tax_type = entities.tax_types[0]
        return JSONConfig(
            version=response.get("version", "1.0"),
            country=country,
            country_name=country_name,
            tax_type=tax_type,
            effective_date=None,
            currency=response.get("currency", "USD"),
            rules=response.get("rules", []),
            metadata=response.get("metadata", {"generated_at": datetime.utcnow().isoformat()})
        )
    
    async def generate_sql_migration(
        self, entities: ExtractedEntities, country: str, country_name: str
    ) -> SQLMigration:
        """Generate SQL migration scripts"""
        entities_json = json.dumps(entities.model_dump(), default=str, indent=2)
        system_prompt, user_prompt = PromptTemplates.get_sql_migration_prompt(
            entities_json=entities_json, country=country, country_name=country_name
        )
        response = await self.ai_processor.process_with_json_response(
            system_prompt=system_prompt, user_prompt=user_prompt
        )
        return self._parse_sql_migration(response)
    
    def _parse_sql_migration(self, response: Dict) -> SQLMigration:
        """Parse AI response into SQLMigration"""
        return SQLMigration(
            migration_name=response.get("migration_name", f"migration_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
            up_script=response.get("up_script", "-- No migration generated"),
            down_script=response.get("down_script", "-- No rollback generated"),
            tables_affected=response.get("tables_affected", []),
            description=response.get("description", "Auto-generated migration")
        )
    
    async def generate_policy_definition(
        self, entities: ExtractedEntities, country: str, country_name: str
    ) -> PolicyDefinition:
        """Generate policy/rules engine definition"""
        entities_json = json.dumps(entities.model_dump(), default=str, indent=2)
        system_prompt, user_prompt = PromptTemplates.get_policy_definition_prompt(
            entities_json=entities_json, country=country, country_name=country_name
        )
        response = await self.ai_processor.process_with_json_response(
            system_prompt=system_prompt, user_prompt=user_prompt
        )
        return self._parse_policy_definition(response)
    
    def _parse_policy_definition(self, response: Dict) -> PolicyDefinition:
        """Parse AI response into PolicyDefinition"""
        return PolicyDefinition(
            policy_name=response.get("policy_name", "tax_policy"),
            version=response.get("version", "1.0"),
            description=response.get("description", "Auto-generated policy"),
            rules=response.get("rules", []),
            metadata=response.get("metadata", {})
        )
    
    async def generate_code(
        self, entities: ExtractedEntities, country: str, country_name: str
    ) -> GeneratedCode:
        """Generate Python code for tax calculations"""
        entities_json = json.dumps(entities.model_dump(), default=str, indent=2)
        system_prompt, user_prompt = PromptTemplates.get_code_generation_prompt(
            entities_json=entities_json, country=country, country_name=country_name
        )
        response = await self.ai_processor.process_with_json_response(
            system_prompt=system_prompt, user_prompt=user_prompt
        )
        return self._parse_generated_code(response, country)
    
    def _parse_generated_code(self, response: Dict, country: str) -> GeneratedCode:
        """Parse AI response into GeneratedCode"""
        return GeneratedCode(
            language="python",
            filename=response.get("filename", f"tax_calculator_{country.lower()}.py"),
            code=response.get("code", "# No code generated"),
            description=response.get("description", "Auto-generated tax calculator"),
            dependencies=response.get("dependencies", [])
        )
