# Configuration Guide

## 📚 Table of Contents
- [Environment Variables](#environment-variables)
- [Model Schema](#model-schema)
- [Supported LLM Providers](#supported-llm-providers)
- [File Processing Options](#file-processing-options)

## Environment Variables

### Required Variables
```bash
# LLM Provider API Key (choose one)
GOOGLE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key
```

### Optional Variables
```bash
# Document Processing
LANGUAGES="fr,en"  # Default: fr
CACHE_DIR="./tmp/cache"  # Default: ./tmp/cache
PDF_STRATEGY="auto"  # Options: auto, hi_res, fast
UNSTRUCTURED_API_KEY=your_key  # Optional, for Unstructured.io

# Monitoring
MONITORING_FILE_PATH="monitoring.json"
COST_MAPPING_PATH="config/cost_mapping.json"
```

## Model Schema
The model schema defines the structure of extracted data. See [Model Schema](MODEL_SCHEMA.md) for details.

## Supported LLM Providers
Currently supported LLM providers:
- Google (Gemini)
- OpenAI
- Anthropic
- Ollama
- Any provider supported by LangChain

## File Processing Options
### PDF Processing Strategies
- `auto`: Automatically choose best strategy
- `hi_res`: High resolution, slower but more accurate
- `fast`: Fast processing, may be less accurate

### Text Extraction Methods
- Unstructured.io (default)
- EasyOCR (coming soon)
- TesseractOCR (coming soon)
