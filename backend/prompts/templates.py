"""
LLM Prompt Templates for Tax Document Processing
"""

from typing import Optional


class PromptTemplates:
    """Collection of prompt templates for different processing stages"""
    
    # ============ Entity Extraction Prompts ============
    
    ENTITY_EXTRACTION_SYSTEM = """You are an expert tax law analyst and data extraction specialist. Your task is to extract structured information from tax and compliance documents.

You must extract the following types of entities:
1. TAX RATES: Standard rates, reduced rates, special rates (as decimals, e.g., 0.17 for 17%)
2. TAX BRACKETS: Progressive tax brackets with min/max amounts and rates
3. THRESHOLDS: Registration thresholds, exemption limits, filing thresholds
4. DEADLINES: Filing deadlines, payment deadlines, reporting periods
5. RULES: Specific tax rules, conditions, exemptions, and special cases

Always respond with valid JSON. Be precise with numbers and dates."""

    ENTITY_EXTRACTION_USER = """Analyze the following tax document and extract all relevant tax entities.

DOCUMENT CONTEXT:
- Country: {country}
- Language: {language}
- Additional Context: {context}

DOCUMENT CONTENT:
{document_text}

Extract and return a JSON object with the following structure:
{{
    "summary": "Brief summary of the document's main tax provisions",
    "tax_types": ["list of tax types mentioned (VAT, INCOME, CORPORATE, etc.)"],
    "rates": [
        {{
            "name": "rate name (e.g., 'standard', 'reduced')",
            "rate": 0.00,
            "description": "description",
            "conditions": ["when this rate applies"],
            "exemptions": ["exemptions from this rate"]
        }}
    ],
    "brackets": [
        {{
            "min_amount": 0,
            "max_amount": null,
            "rate": 0.00,
            "fixed_amount": null
        }}
    ],
    "thresholds": [
        {{
            "name": "threshold name",
            "amount": 0.00,
            "currency": "USD",
            "description": "description",
            "effective_date": "YYYY-MM-DD or null"
        }}
    ],
    "deadlines": [
        {{
            "name": "deadline name",
            "deadline_type": "filing|payment|reporting",
            "frequency": "monthly|quarterly|annually",
            "day_of_period": null,
            "description": "description"
        }}
    ],
    "rules": [
        {{
            "id": "unique_rule_id",
            "name": "rule name",
            "description": "detailed description",
            "tax_type": "VAT|INCOME|CORPORATE|etc",
            "conditions": ["list of conditions"],
            "rate": null,
            "effective_date": "YYYY-MM-DD or null",
            "expiry_date": "YYYY-MM-DD or null",
            "source_reference": "section/article reference"
        }}
    ],
    "confidence_score": 0.0,
    "warnings": ["any uncertainties or ambiguities found"]
}}

Respond ONLY with the JSON object, no additional text."""

    # ============ JSON Config Generation ============
    
    JSON_CONFIG_SYSTEM = """You are a software configuration specialist. Your task is to transform extracted tax entities into clean, machine-readable JSON configuration files that can be used by tax calculation engines."""

    JSON_CONFIG_USER = """Transform the following extracted tax entities into a production-ready JSON configuration.

COUNTRY: {country}
COUNTRY NAME: {country_name}
EXTRACTED ENTITIES:
{entities_json}

Generate a JSON configuration with the following structure:
{{
    "version": "1.0",
    "country": "{country}",
    "country_name": "{country_name}",
    "tax_type": "primary tax type",
    "effective_date": "YYYY-MM-DD or null",
    "currency": "currency code",
    "rules": [
        {{
            "rule_id": "unique_id",
            "name": "rule_name",
            "type": "rate|bracket|threshold|deadline",
            "value": "rate or amount",
            "conditions": {{
                "applies_to": ["categories"],
                "excludes": ["exclusions"],
                "min_amount": null,
                "max_amount": null
            }},
            "effective_from": "date",
            "effective_until": null
        }}
    ],
    "metadata": {{
        "generated_at": "ISO timestamp",
        "source_document": "description",
        "confidence": 0.0
    }}
}}

Respond ONLY with the JSON configuration."""

    # ============ SQL Migration Generation ============
    
    SQL_MIGRATION_SYSTEM = """You are a database migration specialist. Your task is to generate SQL migration scripts for PostgreSQL that implement tax rules extracted from documents. Generate safe, idempotent migrations with proper rollback support."""

    SQL_MIGRATION_USER = """Generate a SQL migration script for the following tax rules.

COUNTRY: {country}
COUNTRY NAME: {country_name}
EXTRACTED ENTITIES:
{entities_json}

Generate a migration with:
1. UP script: Creates/updates tables and inserts data
2. DOWN script: Safely rolls back the changes

Use the following table structures:
- tax_rates (id, country_code, tax_type, rate_name, rate_value, effective_date, expiry_date, conditions JSONB)
- tax_brackets (id, country_code, tax_type, min_amount, max_amount, rate, fixed_amount, effective_date)
- tax_thresholds (id, country_code, threshold_name, amount, currency, effective_date)
- tax_deadlines (id, country_code, deadline_name, deadline_type, frequency, day_of_period, description)

Response format:
{{
    "migration_name": "migration_name_with_timestamp",
    "description": "brief description",
    "tables_affected": ["list of tables"],
    "up_script": "-- UP Migration\\nSQL statements here",
    "down_script": "-- DOWN Migration\\nSQL statements here"
}}

Respond ONLY with the JSON object."""

    # ============ Policy Definition Generation ============
    
    POLICY_DEFINITION_SYSTEM = """You are a rules engine specialist. Your task is to transform tax rules into policy definitions that can be used by compliance engines and rule processors."""

    POLICY_DEFINITION_USER = """Generate a policy definition for the following tax rules.

COUNTRY: {country}
COUNTRY NAME: {country_name}
EXTRACTED ENTITIES:
{entities_json}

Generate a YAML-compatible policy definition with the following structure:
{{
    "policy_name": "descriptive_policy_name",
    "version": "1.0",
    "description": "Policy description",
    "rules": [
        {{
            "rule_id": "unique_id",
            "name": "human readable name",
            "priority": 1,
            "when": {{
                "conditions": [
                    {{"field": "field_name", "operator": "eq|gt|lt|gte|lte|in|not_in", "value": "value"}}
                ],
                "logic": "AND|OR"
            }},
            "then": {{
                "action": "apply_rate|set_value|add_flag",
                "parameters": {{}}
            }},
            "effective_from": "date",
            "effective_until": null
        }}
    ],
    "metadata": {{
        "author": "Tax Code Translator Agent",
        "generated_at": "ISO timestamp",
        "source_country": "{country}"
    }}
}}

Respond ONLY with the JSON object."""

    # ============ Code Generation ============
    
    CODE_GENERATION_SYSTEM = """You are an expert software developer. Your task is to generate clean, well-documented Python code that implements tax calculation logic based on extracted rules."""

    CODE_GENERATION_USER = """Generate Python code that implements the following tax rules.

COUNTRY: {country}
COUNTRY NAME: {country_name}
EXTRACTED ENTITIES:
{entities_json}

Generate a Python module with:
1. Data classes for tax configurations
2. Calculator class with methods for each tax type
3. Validation functions
4. Example usage in docstrings

Response format:
{{
    "filename": "tax_calculator_{country_lower}.py",
    "description": "Tax calculator for {country_name}",
    "dependencies": ["list of pip packages needed"],
    "code": "full Python code here"
}}

Requirements:
- Use type hints
- Include docstrings
- Handle edge cases
- Include unit test examples in docstrings

Respond ONLY with the JSON object."""

    # ============ Helper Methods ============
    
    @classmethod
    def get_entity_extraction_prompt(
        cls,
        document_text: str,
        country: str,
        language: str = "en",
        context: Optional[str] = None
    ) -> tuple[str, str]:
        """Get the entity extraction prompt pair"""
        user_prompt = cls.ENTITY_EXTRACTION_USER.format(
            document_text=document_text,
            country=country,
            language=language,
            context=context or "No additional context provided"
        )
        return cls.ENTITY_EXTRACTION_SYSTEM, user_prompt
    
    @classmethod
    def get_json_config_prompt(
        cls,
        entities_json: str,
        country: str,
        country_name: str
    ) -> tuple[str, str]:
        """Get the JSON config generation prompt pair"""
        user_prompt = cls.JSON_CONFIG_USER.format(
            entities_json=entities_json,
            country=country,
            country_name=country_name
        )
        return cls.JSON_CONFIG_SYSTEM, user_prompt
    
    @classmethod
    def get_sql_migration_prompt(
        cls,
        entities_json: str,
        country: str,
        country_name: str
    ) -> tuple[str, str]:
        """Get the SQL migration generation prompt pair"""
        user_prompt = cls.SQL_MIGRATION_USER.format(
            entities_json=entities_json,
            country=country,
            country_name=country_name
        )
        return cls.SQL_MIGRATION_SYSTEM, user_prompt
    
    @classmethod
    def get_policy_definition_prompt(
        cls,
        entities_json: str,
        country: str,
        country_name: str
    ) -> tuple[str, str]:
        """Get the policy definition generation prompt pair"""
        user_prompt = cls.POLICY_DEFINITION_USER.format(
            entities_json=entities_json,
            country=country,
            country_name=country_name
        )
        return cls.POLICY_DEFINITION_SYSTEM, user_prompt
    
    @classmethod
    def get_code_generation_prompt(
        cls,
        entities_json: str,
        country: str,
        country_name: str
    ) -> tuple[str, str]:
        """Get the code generation prompt pair"""
        user_prompt = cls.CODE_GENERATION_USER.format(
            entities_json=entities_json,
            country=country,
            country_name=country_name,
            country_lower=country.lower()
        )
        return cls.CODE_GENERATION_SYSTEM, user_prompt
