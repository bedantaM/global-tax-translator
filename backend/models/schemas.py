"""
Pydantic models for the Tax-Code Translator Agent
"""

from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field


class TaxType(str, Enum):
    """Types of taxes supported"""
    VAT = "VAT"
    INCOME = "INCOME"
    CORPORATE = "CORPORATE"
    SALES = "SALES"
    WITHHOLDING = "WITHHOLDING"
    CUSTOMS = "CUSTOMS"
    EXCISE = "EXCISE"
    PROPERTY = "PROPERTY"
    PAYROLL = "PAYROLL"
    OTHER = "OTHER"


class OutputFormat(str, Enum):
    """Supported output formats"""
    JSON = "json"
    YAML = "yaml"
    SQL = "sql"
    CODE = "code"
    ALL = "all"


class DocumentType(str, Enum):
    """Types of documents supported"""
    PDF = "pdf"
    TEXT = "text"
    DOCX = "docx"


# ============ Input Models ============

class ProcessRequest(BaseModel):
    """Request model for document processing"""
    country: str = Field(..., description="ISO country code (e.g., BR, DE, US)")
    document_type: Optional[DocumentType] = Field(None, description="Type of document")
    output_format: OutputFormat = Field(default=OutputFormat.ALL, description="Desired output format")
    language: Optional[str] = Field(None, description="Source language (auto-detected if not provided)")
    context: Optional[str] = Field(None, description="Additional context about the document")


class TextProcessRequest(BaseModel):
    """Request model for processing raw text"""
    text: str = Field(..., description="Raw text content to process")
    country: str = Field(..., description="ISO country code")
    output_format: OutputFormat = Field(default=OutputFormat.ALL)
    language: Optional[str] = None
    context: Optional[str] = None


# ============ Tax Entity Models ============

class TaxRate(BaseModel):
    """Individual tax rate definition"""
    name: str = Field(..., description="Name of the rate (e.g., 'standard', 'reduced')")
    rate: float = Field(..., ge=0, le=1, description="Tax rate as decimal (e.g., 0.17 for 17%)")
    description: Optional[str] = None
    conditions: List[str] = Field(default_factory=list, description="Conditions when this rate applies")
    exemptions: List[str] = Field(default_factory=list, description="Exemptions from this rate")


class TaxBracket(BaseModel):
    """Tax bracket for progressive taxes"""
    min_amount: float = Field(..., ge=0)
    max_amount: Optional[float] = Field(None, description="None means unlimited")
    rate: float = Field(..., ge=0, le=1)
    fixed_amount: Optional[float] = Field(None, description="Fixed amount to add")


class TaxThreshold(BaseModel):
    """Threshold definition"""
    name: str
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    effective_date: Optional[date] = None


class TaxDeadline(BaseModel):
    """Filing or payment deadline"""
    name: str
    deadline_type: str = Field(..., description="filing, payment, reporting")
    frequency: str = Field(..., description="monthly, quarterly, annually")
    day_of_period: Optional[int] = Field(None, description="Day of month/quarter")
    description: Optional[str] = None


class TaxRule(BaseModel):
    """Individual tax rule definition"""
    id: str
    name: str
    description: str
    tax_type: TaxType
    conditions: List[str] = Field(default_factory=list)
    rate: Optional[float] = None
    brackets: Optional[List[TaxBracket]] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    source_reference: Optional[str] = Field(None, description="Reference to source document section")


class ExtractedEntities(BaseModel):
    """All entities extracted from a document"""
    tax_types: List[TaxType] = Field(default_factory=list)
    rates: List[TaxRate] = Field(default_factory=list)
    brackets: List[TaxBracket] = Field(default_factory=list)
    thresholds: List[TaxThreshold] = Field(default_factory=list)
    deadlines: List[TaxDeadline] = Field(default_factory=list)
    rules: List[TaxRule] = Field(default_factory=list)
    raw_extractions: Dict[str, Any] = Field(default_factory=dict, description="Additional extracted data")


# ============ Output Models ============

class JSONConfig(BaseModel):
    """JSON configuration output"""
    version: str = "1.0"
    country: str
    country_name: str
    tax_type: TaxType
    effective_date: Optional[date] = None
    currency: str = "USD"
    rules: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SQLMigration(BaseModel):
    """SQL migration output"""
    migration_name: str
    up_script: str = Field(..., description="SQL to apply migration")
    down_script: str = Field(..., description="SQL to rollback migration")
    tables_affected: List[str] = Field(default_factory=list)
    description: str


class PolicyDefinition(BaseModel):
    """Policy/rules engine definition"""
    policy_name: str
    version: str = "1.0"
    description: str
    rules: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GeneratedCode(BaseModel):
    """Generated code output"""
    language: str = "python"
    filename: str
    code: str
    description: str
    dependencies: List[str] = Field(default_factory=list)


class ProcessingResult(BaseModel):
    """Complete processing result"""
    success: bool
    document_id: str
    country: str
    country_name: str
    language_detected: str
    processing_time_ms: int
    
    # Extracted data
    summary: str
    entities: ExtractedEntities
    
    # Generated outputs
    json_config: Optional[JSONConfig] = None
    sql_migration: Optional[SQLMigration] = None
    policy_definition: Optional[PolicyDefinition] = None
    generated_code: Optional[GeneratedCode] = None
    
    # Metadata
    confidence_score: float = Field(..., ge=0, le=1)
    warnings: List[str] = Field(default_factory=list)
    source_sections: List[str] = Field(default_factory=list, description="Relevant sections from source")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


# ============ Health & Status Models ============

class HealthStatus(BaseModel):
    """API health status"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
