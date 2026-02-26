"""
Global Tax-Code Translator Agent API
FastAPI application for processing tax documents
"""

import os
import sys
import uuid
import time
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.schemas import (
    ProcessingResult, ErrorResponse, HealthStatus,
    OutputFormat, TextProcessRequest, ExtractedEntities
)
from services.document_parser import DocumentParser
from services.ai_processor import AIProcessor, MockAIProcessor
from services.entity_extractor import EntityExtractor
from services.output_generator import OutputGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Global Tax-Code Translator Agent",
    description="AI-powered agent that transforms tax documents into machine-readable formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_parser = DocumentParser()

# Use mock processor if no API key is set (for demo purposes)
if os.getenv("OPENAI_API_KEY"):
    ai_processor = AIProcessor()
    logger.info("Using OpenAI API for processing")
else:
    ai_processor = MockAIProcessor()
    logger.warning("No OPENAI_API_KEY set. Using mock processor for demo.")

entity_extractor = EntityExtractor(ai_processor)
output_generator = OutputGenerator(ai_processor)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Global Tax-Code Translator Agent",
        "version": "1.0.0",
        "description": "Transform tax documents into machine-readable formats",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "process_file": "POST /api/process",
            "process_text": "POST /api/process-text"
        }
    }


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    ai_status = await ai_processor.health_check()
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "document_parser": "healthy",
            "ai_processor": ai_status.get("status", "unknown"),
            "entity_extractor": "healthy",
            "output_generator": "healthy"
        }
    )


@app.post("/api/process", response_model=ProcessingResult)
async def process_document(
    file: UploadFile = File(...),
    country: str = Form(..., description="ISO country code (e.g., BR, DE, US)"),
    output_format: OutputFormat = Form(default=OutputFormat.ALL),
    language: Optional[str] = Form(default=None),
    context: Optional[str] = Form(default=None)
):
    """
    Process a tax document and generate machine-readable outputs
    """
    start_time = time.time()
    document_id = str(uuid.uuid4())
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        # Check file size
        max_size = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB")
        
        # Parse document
        logger.info(f"Processing document: {file.filename} for country: {country}")
        text, metadata = await document_parser.parse(content, file.filename)
        text = document_parser.clean_text(text)
        
        # Detect language if not provided
        if not language:
            language = document_parser.detect_language(text)
        
        # Get country name
        country_name = ai_processor.get_country_name(country.upper())
        
        # Check if document is too large and needs chunking
        token_count = await ai_processor.estimate_tokens(text)
        
        if token_count > 6000:
            # Chunk the document
            chunks = await ai_processor.chunk_text(text, max_tokens=6000)
            entities, raw_responses = await entity_extractor.extract_from_chunks(
                chunks=chunks, country=country, language=language, context=context
            )
        else:
            # Process as single document
            entities, raw_response = await entity_extractor.extract(
                document_text=text, country=country, language=language, context=context
            )
        
        # Validate entities
        warnings = entity_extractor.validate_entities(entities)
        
        # Generate outputs based on requested format
        outputs = {}
        if output_format in [OutputFormat.ALL, OutputFormat.JSON]:
            outputs["json_config"] = await output_generator.generate_json_config(
                entities, country.upper(), country_name
            )
        if output_format in [OutputFormat.ALL, OutputFormat.SQL]:
            outputs["sql_migration"] = await output_generator.generate_sql_migration(
                entities, country.upper(), country_name
            )
        if output_format in [OutputFormat.ALL, OutputFormat.YAML]:
            outputs["policy_definition"] = await output_generator.generate_policy_definition(
                entities, country.upper(), country_name
            )
        if output_format in [OutputFormat.ALL, OutputFormat.CODE]:
            outputs["generated_code"] = await output_generator.generate_code(
                entities, country.upper(), country_name
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ProcessingResult(
            success=True,
            document_id=document_id,
            country=country.upper(),
            country_name=country_name,
            language_detected=language,
            processing_time_ms=processing_time,
            summary=entities.raw_extractions.get("summary", "Document processed successfully"),
            entities=entities,
            json_config=outputs.get("json_config"),
            sql_migration=outputs.get("sql_migration"),
            policy_definition=outputs.get("policy_definition"),
            generated_code=outputs.get("generated_code"),
            confidence_score=entities.raw_extractions.get("confidence_score", 0.8),
            warnings=warnings + entities.raw_extractions.get("warnings", []),
            source_sections=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process-text", response_model=ProcessingResult)
async def process_text(request: TextProcessRequest):
    """
    Process raw text and generate machine-readable outputs
    """
    start_time = time.time()
    document_id = str(uuid.uuid4())
    
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Empty text provided")
        
        # Clean text
        text = document_parser.clean_text(request.text)
        
        # Detect language if not provided
        language = request.language or document_parser.detect_language(text)
        
        # Get country name
        country_name = ai_processor.get_country_name(request.country.upper())
        
        # Extract entities
        entities, raw_response = await entity_extractor.extract(
            document_text=text,
            country=request.country,
            language=language,
            context=request.context
        )
        
        # Validate entities
        warnings = entity_extractor.validate_entities(entities)
        
        # Generate outputs
        outputs = {}
        if request.output_format in [OutputFormat.ALL, OutputFormat.JSON]:
            outputs["json_config"] = await output_generator.generate_json_config(
                entities, request.country.upper(), country_name
            )
        if request.output_format in [OutputFormat.ALL, OutputFormat.SQL]:
            outputs["sql_migration"] = await output_generator.generate_sql_migration(
                entities, request.country.upper(), country_name
            )
        if request.output_format in [OutputFormat.ALL, OutputFormat.YAML]:
            outputs["policy_definition"] = await output_generator.generate_policy_definition(
                entities, request.country.upper(), country_name
            )
        if request.output_format in [OutputFormat.ALL, OutputFormat.CODE]:
            outputs["generated_code"] = await output_generator.generate_code(
                entities, request.country.upper(), country_name
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ProcessingResult(
            success=True,
            document_id=document_id,
            country=request.country.upper(),
            country_name=country_name,
            language_detected=language,
            processing_time_ms=processing_time,
            summary=entities.raw_extractions.get("summary", "Text processed successfully"),
            entities=entities,
            json_config=outputs.get("json_config"),
            sql_migration=outputs.get("sql_migration"),
            policy_definition=outputs.get("policy_definition"),
            generated_code=outputs.get("generated_code"),
            confidence_score=entities.raw_extractions.get("confidence_score", 0.8),
            warnings=warnings + entities.raw_extractions.get("warnings", []),
            source_sections=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            error_code="INTERNAL_ERROR",
            details={"type": type(exc).__name__}
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=True)
