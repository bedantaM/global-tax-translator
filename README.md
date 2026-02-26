# Global Tax-Code Translator Agent 🌍⚖️

An AI-powered agent that transforms complex tax and compliance documents into machine-readable formats, database schemas, and executable code.

## 🎯 Problem Statement

When expanding to a new country, massive engineering effort is spent manually translating complex tax/compliance documents (often in local languages) into technical schema, database rules, and code logic. This process is error-prone and slow.

## 💡 Solution

An AI agent that:
1. **Ingests** raw regulatory documents (PDFs, text files)
2. **Extracts** key entities (tax rates, thresholds, conditions, deadlines)
3. **Transforms** them into structured, machine-readable formats
4. **Generates** draft migration scripts and policy definitions

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Document       │     │  AI Processing   │     │  Output Generation  │
│  Ingestion      │────▶│  Engine          │────▶│  Layer              │
│  (PDF/Text)     │     │  (LLM + NLP)     │     │  (JSON/SQL/Code)    │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────────┐
                                                 │  Review Dashboard   │
                                                 │  (Web UI)           │
                                                 └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend)
- OpenAI API Key

### Installation

```bash
# Clone the repository
cd "Global Tax code"

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the backend
uvicorn main:app --reload --port 8000

# Frontend setup (in a new terminal)
cd ../frontend
npm install
npm run dev
```

### Using the API

```bash
# Upload and process a document
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@sample_tax_document.pdf" \
  -F "country=brazil" \
  -F "output_format=all"
```

## 📁 Project Structure

```
Global Tax code/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── services/
│   │   ├── document_parser.py  # PDF/text extraction
│   │   ├── ai_processor.py     # LLM integration
│   │   ├── entity_extractor.py # Tax entity extraction
│   │   └── output_generator.py # Schema/code generation
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── prompts/
│       └── templates.py        # LLM prompt templates
├── frontend/
│   ├── index.html             # Web UI
│   ├── styles.css             # Styling
│   └── app.js                 # Frontend logic
├── samples/
│   ├── brazil_tax_update.txt  # Sample document
│   └── eu_vat_rules.txt       # Sample document
└── README.md
```

## 🔧 Output Formats

### 1. JSON Configuration
```json
{
  "country": "BR",
  "tax_type": "VAT",
  "rules": [
    {
      "name": "standard_rate",
      "rate": 0.17,
      "conditions": ["goods", "services"]
    }
  ]
}
```

### 2. SQL Migration
```sql
INSERT INTO tax_rates (country, tax_type, rate, effective_date)
VALUES ('BR', 'ICMS', 0.17, '2024-01-01');
```

### 3. Policy Definition
```yaml
policy:
  name: brazil_icms_2024
  rules:
    - when: transaction.type == "goods"
      apply: rate * 0.17
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **AI/LLM**: OpenAI GPT-4
- **Document Processing**: pdfplumber, pytesseract
- **Frontend**: Vanilla JS, HTML, CSS
- **Deployment**: Docker, any cloud platform

## 📄 License

MIT License
