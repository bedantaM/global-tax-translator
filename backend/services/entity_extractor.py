"""
Entity Extractor Service
Extracts tax entities from documents using AI processing
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import date

from ..models.schemas import (
    ExtractedEntities,
    TaxRate,
    TaxBracket,
    TaxThreshold,
    TaxDeadline,
    TaxRule,
    TaxType
)
from ..prompts.templates import PromptTemplates
from .ai_processor import AIProcessor

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Service for extracting tax entities from document text"""
    
    def __init__(self, ai_processor: AIProcessor):
        """
        Initialize Entity Extractor
        
        Args:
            ai_processor: AI processor instance for LLM calls
        """
        self.ai_processor = ai_processor
    
    async def extract(
        self,
        document_text: str,
        country: str,
        language: str = "en",
        context: Optional[str] = None
    ) -> tuple[ExtractedEntities, Dict[str, Any]]:
        """
        Extract tax entities from document text
        
        Args:
            document_text: Cleaned document text
            country: ISO country code
            language: Document language
            context: Additional context
            
        Returns:
            Tuple of (ExtractedEntities, raw_response)
        """
        # Get prompts
        system_prompt, user_prompt = PromptTemplates.get_entity_extraction_prompt(
            document_text=document_text,
            country=country,
            language=language,
            context=context
        )
        
        # Process with AI
        raw_response = await self.ai_processor.process_with_json_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=4096
        )
        
        # Parse and validate response
        entities = self._parse_extraction_response(raw_response)
        
        return entities, raw_response
    
    def _parse_extraction_response(self, response: Dict[str, Any]) -> ExtractedEntities:
        """
        Parse AI response into ExtractedEntities model
        
        Args:
            response: Raw AI response dict
            
        Returns:
            ExtractedEntities object
        """
        # Parse tax types
        tax_types = []
        for tax_type_str in response.get("tax_types", []):
            try:
                tax_type = TaxType(tax_type_str.upper())
                tax_types.append(tax_type)
            except ValueError:
                logger.warning(f"Unknown tax type: {tax_type_str}")
                tax_types.append(TaxType.OTHER)
        
        # Parse rates
        rates = []
        for rate_data in response.get("rates", []):
            try:
                rate = TaxRate(
                    name=rate_data.get("name", "unknown"),
                    rate=float(rate_data.get("rate", 0)),
                    description=rate_data.get("description"),
                    conditions=rate_data.get("conditions", []),
                    exemptions=rate_data.get("exemptions", [])
                )
                rates.append(rate)
            except Exception as e:
                logger.warning(f"Failed to parse rate: {e}")
        
        # Parse brackets
        brackets = []
        for bracket_data in response.get("brackets", []):
            try:
                bracket = TaxBracket(
                    min_amount=float(bracket_data.get("min_amount", 0)),
                    max_amount=bracket_data.get("max_amount"),
                    rate=float(bracket_data.get("rate", 0)),
                    fixed_amount=bracket_data.get("fixed_amount")
                )
                brackets.append(bracket)
            except Exception as e:
                logger.warning(f"Failed to parse bracket: {e}")
        
        # Parse thresholds
        thresholds = []
        for threshold_data in response.get("thresholds", []):
            try:
                threshold = TaxThreshold(
                    name=threshold_data.get("name", "unknown"),
                    amount=float(threshold_data.get("amount", 0)),
                    currency=threshold_data.get("currency", "USD"),
                    description=threshold_data.get("description"),
                    effective_date=self._parse_date(threshold_data.get("effective_date"))
                )
                thresholds.append(threshold)
            except Exception as e:
                logger.warning(f"Failed to parse threshold: {e}")
        
        # Parse deadlines
        deadlines = []
        for deadline_data in response.get("deadlines", []):
            try:
                deadline = TaxDeadline(
                    name=deadline_data.get("name", "unknown"),
                    deadline_type=deadline_data.get("deadline_type", "filing"),
                    frequency=deadline_data.get("frequency", "annually"),
                    day_of_period=deadline_data.get("day_of_period"),
                    description=deadline_data.get("description")
                )
                deadlines.append(deadline)
            except Exception as e:
                logger.warning(f"Failed to parse deadline: {e}")
        
        # Parse rules
        rules = []
        for rule_data in response.get("rules", []):
            try:
                # Get tax type
                tax_type_str = rule_data.get("tax_type", "OTHER")
                try:
                    tax_type = TaxType(tax_type_str.upper())
                except ValueError:
                    tax_type = TaxType.OTHER
                
                rule = TaxRule(
                    id=rule_data.get("id", f"rule_{len(rules)}"),
                    name=rule_data.get("name", "unknown"),
                    description=rule_data.get("description", ""),
                    tax_type=tax_type,
                    conditions=rule_data.get("conditions", []),
                    rate=rule_data.get("rate"),
                    brackets=None,  # Would need separate parsing
                    effective_date=self._parse_date(rule_data.get("effective_date")),
                    expiry_date=self._parse_date(rule_data.get("expiry_date")),
                    source_reference=rule_data.get("source_reference")
                )
                rules.append(rule)
            except Exception as e:
                logger.warning(f"Failed to parse rule: {e}")
        
        return ExtractedEntities(
            tax_types=tax_types,
            rates=rates,
            brackets=brackets,
            thresholds=thresholds,
            deadlines=deadlines,
            rules=rules,
            raw_extractions={
                "summary": response.get("summary", ""),
                "confidence_score": response.get("confidence_score", 0.0),
                "warnings": response.get("warnings", [])
            }
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse date string to date object
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            date object or None
        """
        if not date_str or date_str.lower() == "null":
            return None
        
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return None
    
    async def extract_from_chunks(
        self,
        chunks: list[str],
        country: str,
        language: str = "en",
        context: Optional[str] = None
    ) -> tuple[ExtractedEntities, list[Dict[str, Any]]]:
        """
        Extract entities from multiple document chunks and merge results
        
        Args:
            chunks: List of document text chunks
            country: ISO country code
            language: Document language
            context: Additional context
            
        Returns:
            Tuple of (merged ExtractedEntities, list of raw responses)
        """
        all_entities = []
        all_responses = []
        
        for i, chunk in enumerate(chunks):
            chunk_context = f"{context or ''} [Chunk {i+1} of {len(chunks)}]"
            entities, response = await self.extract(
                document_text=chunk,
                country=country,
                language=language,
                context=chunk_context
            )
            all_entities.append(entities)
            all_responses.append(response)
        
        # Merge all extracted entities
        merged = self._merge_entities(all_entities)
        
        return merged, all_responses
    
    def _merge_entities(self, entities_list: list[ExtractedEntities]) -> ExtractedEntities:
        """
        Merge multiple ExtractedEntities objects
        
        Args:
            entities_list: List of ExtractedEntities
            
        Returns:
            Merged ExtractedEntities
        """
        merged = ExtractedEntities(
            tax_types=[],
            rates=[],
            brackets=[],
            thresholds=[],
            deadlines=[],
            rules=[],
            raw_extractions={}
        )
        
        seen_tax_types = set()
        seen_rate_names = set()
        seen_threshold_names = set()
        seen_deadline_names = set()
        seen_rule_ids = set()
        
        for entities in entities_list:
            # Merge tax types (unique)
            for tax_type in entities.tax_types:
                if tax_type not in seen_tax_types:
                    merged.tax_types.append(tax_type)
                    seen_tax_types.add(tax_type)
            
            # Merge rates (unique by name)
            for rate in entities.rates:
                if rate.name not in seen_rate_names:
                    merged.rates.append(rate)
                    seen_rate_names.add(rate.name)
            
            # Merge brackets (all)
            merged.brackets.extend(entities.brackets)
            
            # Merge thresholds (unique by name)
            for threshold in entities.thresholds:
                if threshold.name not in seen_threshold_names:
                    merged.thresholds.append(threshold)
                    seen_threshold_names.add(threshold.name)
            
            # Merge deadlines (unique by name)
            for deadline in entities.deadlines:
                if deadline.name not in seen_deadline_names:
                    merged.deadlines.append(deadline)
                    seen_deadline_names.add(deadline.name)
            
            # Merge rules (unique by ID)
            for rule in entities.rules:
                if rule.id not in seen_rule_ids:
                    merged.rules.append(rule)
                    seen_rule_ids.add(rule.id)
            
            # Merge raw extractions
            for key, value in entities.raw_extractions.items():
                if key not in merged.raw_extractions:
                    merged.raw_extractions[key] = value
                elif isinstance(value, list):
                    if isinstance(merged.raw_extractions[key], list):
                        merged.raw_extractions[key].extend(value)
        
        return merged
    
    def validate_entities(self, entities: ExtractedEntities) -> list[str]:
        """
        Validate extracted entities and return warnings
        
        Args:
            entities: Extracted entities to validate
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for rates outside normal range
        for rate in entities.rates:
            if rate.rate > 0.5:
                warnings.append(f"Unusually high rate detected: {rate.name} = {rate.rate*100}%")
            if rate.rate < 0:
                warnings.append(f"Negative rate detected: {rate.name} = {rate.rate*100}%")
        
        # Check for brackets with invalid ranges
        for i, bracket in enumerate(entities.brackets):
            if bracket.max_amount and bracket.min_amount > bracket.max_amount:
                warnings.append(f"Invalid bracket range at position {i}")
        
        # Check for missing required fields in rules
        for rule in entities.rules:
            if not rule.description:
                warnings.append(f"Rule '{rule.id}' missing description")
        
        # Check for duplicate names
        rate_names = [r.name for r in entities.rates]
        if len(rate_names) != len(set(rate_names)):
            warnings.append("Duplicate rate names detected")
        
        return warnings
