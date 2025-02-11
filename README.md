# 📊 Extrix - Data Information Extractor

## 🎯 Overview
Extrix is a tool that simplify data extraction from documents (PDF, Word, etc.) and outputs structured data in `.json` or `.csv` format. It uses a language model (LLM) to get best understanding of the context and extract data.

Example of output from `data/Bail 3.PDF`
```json
[
  {
    "bailleur": "François Girard",
    "preneur": "Maison du Livre",
    "adresse": "4 Rue de l'Académie, 75009 Paris",
    "description": "une grande salle de vente, un bureau et des sanitaires | usage: librairie",
    "surface": 60.0,
    "date_prise_effet": {
      "day": 1,
      "month": 6,
      "year": 2025
    },
    "date_fin": {
      "day": 31,
      "month": 5,
      "year": 2034
    },
    "duree_bail": {
      "years": 9,
      "months": 0
    }
  }
]
```

## ✨ Features

- [X] Data extraction from documents (Text based or scanned image)
- [X] Structured output `.json` or `.csv`
- [X] Output validation with a model schema (Pyndatic Model or JSON Schema)
- [X] Multi-language support
- [X] Multiple document processing options (Unstructured, EasyOCR, TesserOCR)
- [X] CLI Tool
- [X] LLM that support tooling integrations for data extraction
- [X] LLM monitoring (tokens consumption, cost estimation, etc.)
- [ ] LLM that not support tooling integrations for data extraction
- [ ] Vision Language Model (VLM) support
- [ ] Web API
- [ ] Python library
- [ ] Docker container
- [ ] ...

## 📚 Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Contribution](#contribution)
- [License](#license)

## 🚀 Installation
### 📋 Requirements
- Python 3.10 or higher
- Pip, Virtualenv
- Libmagic, Poppler, Tesseract

Example of installation on macOS
```bash
brew install libmagic poppler tesseract
```

### 🔧 Steps
Clone the repository using `git` or download the zip file
```bash
git clone https://github.com/mendrika261/data-extraction.git
```
Get inside the project directory
```bash
cd data-extraction
```
Create a virtual environment
```bash
python -m venv venv
```
Activate the virtual environment
```bash
source venv/bin/activate
```
Install dependencies
```bash
pip install -r requirements.txt
```

## 💡 Usage
### 📐 Create a model
Model is a schema that defines the structure of the output data. It is used to validate the output data. It can be a Pydantic model or a JSON schema.

> Description of each field in the model is important to help the LLM to understand the context and extract data.

#### Example of a model schema for a leasing contract
##### 📄 Json model (`config/model.json`)
```json
{
    "name": "Leasing",
    "description": "Informations extraites d'un contrat de location",
    "fields": {
        "bailleur": {
            "field_type": "str",
            "title": "Bailleur",
            "description": "Nom de la société UNIQUEMENT ou prénom nom de la personne UNIQUEMENT",
            "required": true
        },
        "preneur": {
            "field_type": "str",
            "title": "Preneur",
            "description": "Nom de la société UNIQUEMENT ou prénom nom de la personne UNIQUEMENT",
            "required": true
        },
        "adresse": {
            "field_type": "str",
            "title": "Adresse du bien loué",
            "description": "Numéro, rue, code postal, ville",
            "required": true
        },
        "description": {
            "field_type": "str",
            "title": "Description du bien et type d'usage",
            "description": "Description sous forme de liste, et types d'usage à la fin uniquement, pas de phrases",
            "required": true
        },
        "surface": {
            "field_type": "float",
            "title": "Surface",
            "description": "Surface du bien loué en m²",
            "required": true
        },
        "date_prise_effet": {
            "field_type": "date",
            "title": "Date de prise d'effet",
            "description": "Date de prise d'effet du bail",
            "required": true
        },
        "date_fin": {
            "field_type": "date",
            "title": "Date de fin",
            "description": "Date de fin du bail",
            "required": true,
            "validators": [
                {
                    "type": "registered",
                    "name": "date_after",
                    "params": {
                        "field": "date_prise_effet"
                    }
                }
            ]
        },
        "duree_bail": {
            "field_type": "delay",
            "title": "Durée du bail",
            "description": "Durée du bail en années et mois",
            "required": true,
            "validators": [
                {
                    "type": "registered",
                    "name": "delay_matches_dates",
                    "params": {
                        "start_date": "date_prise_effet",
                        "end_date": "date_fin"
                    }
                }
            ]
        }
    }
}
```
##### 🐍 Pydantic model
```python
class Leasing(BaseModel):
    bailleur: str = Field(
        ..., 
        title="Bailleur",
        description="Nom de la société UNIQUEMENT ou prénom nom de la personne UNIQUEMENT"
    )
    preneur: str = Field(
        ..., 
        title="Preneur",
        description="Nom de la société UNIQUEMENT ou prénom nom de la personne UNIQUEMENT"
    )
    adresse: str = Field(
        ..., 
        title="Adresse du bien loué",
        description="Numéro, rue, code postal, ville"
    )
    description: str = Field(
        ..., 
        title="Description du bien",
        description="Description sous forme de liste, avec usages et équipements inclus, pas de phrases"
    )
    surface: float = Field(
        ..., 
        title="Surface",
        description="Surface du bien loué en m²"
    )
    date_prise_effet: Date = Field(
        ..., 
        title="Date de prise d'effet",
        description="Date de prise d'effet du bail"
    )
    date_fin: Date = Field(
        ..., 
        title="Date de fin",
        description="Date de fin du bail"
    )
    duree_bail: Delay = Field(
        ..., 
        title="Durée du bail",
        description="Durée du bail en années et mois"
    )

    @field_validator('date_fin')
    def validate_date_fin(cls, v: Date, info: ValidationInfo) -> datetime:
        # implementation
        pass
    
    @field_validator('duree_bail')
    def validate_duree_bail(cls, v: Delay, info: ValidationInfo) -> Delay:
        # implementation
        pass

    model_config = {
        "json_schema_extra": {
            "description": "Informations extraites d'un contrat de location"
        }
    }
```
### 📝 Examples (optional)
Examples is another way to help the LLM to understand the context and extract data. It is json file that contains examples of the output data.

> Role `assistant` is used to indicate the output of the LLM. You can also use role `user` to indicate the input data. See [Message concept](https://python.langchain.com/docs/concepts/messages/#role) for more details.

Examples for a leasing contract according to the model above (`data/examples.json`)
```json
{
    "examples": [
        {
            "role": "assistant",
            "content": {
                "bailleur": "Nvidia",
                "preneur": "Jean Dupont",
                "adresse": "12 rue de la paix, 75000 Paris",
                "description": "Appartement de 3 pièces, 2 chambres, 1 salle de bain, 1 cuisine, 1 salon | usage: habitation uniquement",
                "surface": 50.0,
                "date_prise_effet": {
                    "year": 2022,
                    "month": 1,
                    "day": 31
                },
                "date_fin": {
                    "year": 2023,
                    "month": 1,
                    "day": 31
                },
                "duree_bail": {
                    "years": 1
                }
            }
        }
    ]
}
```
### ⚙️ Set the configuration (`.env`)
Create a `.env` file in the project directory and set the configuration. You can use the `.env.example` file as a template.
> For now, all providers from [here](https://python.langchain.com/docs/integrations/providers/all/) and LLM *with tooling integrations* are supported.
```bash
# File processing configuration
LANGUAGES = "fr"
CACHE_DIR = "./tmp/cache"
# Set the API key for unstructured API if you want to use it
# UNSTRUCTURED_API_KEY = 
PDF_STRATEGY = "auto"

# LLM configuration
# Api keys for any supported LLM provider (e.g., google-genai, ollama SEE langchain providers documentation for the name of the variables)
GOOGLE_API_KEY = 

# Monitoring
MONITORING_FILE_PATH = "monitoring.json"
COST_MAPPING_PATH = "config/cost_mapping.json"
TOKENS_INPUT_PRICING_UNIT = 1000000
TOKENS_OUTPUT_PRICING_UNIT = 1000000
```

### 🖥️ Run the CLI tool
Basic usage of the CLI tool, see [Configuration](#configuration) for more details.
> The path can be a file or a glob pattern (e.g., `data/*.pdf`)
```bash
python cli.py "data/BAIL 3.pdf"
```

### 📊 Monitoring LLM usage
The monitoring file is a JSON file that contains the usage of the LLM. It can be set using the `MONITORING_FILE_PATH` in the `.env` file.

The cost is based on the actual pricing of the LLM provider. The cost mapping can be updated in `config/cost_mapping.json`.

Example of monitoring file
```json
[
  {
    "timestamp": "2025-02-10T23:23:22.340297",
    "model": "gemini-1.5-flash",
    "provider": "google-genai",
    "duration_seconds": 393.38787699999995,
    "input_tokens": 175982,
    "output_tokens": 25027,
    "total_tokens": 200009,
    "estimated_cost_usd": "xxx"
  },
  {
    "timestamp": "2025-02-11T00:40:50.692436",
    "model": "gemini-1.5-pro",
    "provider": "google-genai",
    "duration_seconds": 24.356106,
    "input_tokens": 6984,
    "output_tokens": 429,
    "total_tokens": 7413,
    "estimated_cost_usd": "xxx"
  }
]
```

## ⚙️ Configuration
```bash
usage: cli.py [-h] [--languages LANGUAGES [LANGUAGES ...]] [--strategy {auto,hi_res,fast}]
              [--no-cache] [--processor {unstructured,easyocr,tesserocr}] [--model MODEL]
              [--provider PROVIDER] [--temperature TEMPERATURE] [--examples EXAMPLES]
              [--model-schema MODEL_SCHEMA] [--output OUTPUT]
              input_pattern

Extract structured data from documents

options:
  -h, --help                            show this help message and exit

Input Configuration:
  input_pattern                         Path or glob pattern for document files
  --languages LANGUAGES [LANGUAGES ...]
                                        List of languages (default: ['fr'])
  --strategy {auto,hi_res,fast}
  --no-cache
  --processor {unstructured,easyocr,tesserocr}

LLM Configuration:
  --model MODEL                         LLM model name to use for extraction (default:
                                        gemini-1.5-pro)
  --provider PROVIDER                   LLM provider (e.g., google-genai, ollama) (default: google-
                                        genai)
  --temperature TEMPERATURE             LLM temperature setting - lower values are more focused
                                        (default: 0.1)

Model Configuration:
  --examples EXAMPLES                   Path to examples JSON file for few-shot learning (default:
                                        data/examples.json)
  --model-schema MODEL_SCHEMA           Path to model schema JSON file defining the extraction
                                        structure (default: config/model.json)

Output Configuration:
  --output OUTPUT                       Output file path (supported formats: CSV, JSON)
```

## 📚 Documentation
### 🎯 Concept
There are two main processes in the project: the **content extraction** and the **structured data extraction**.
- The **content extraction** is the process of extracting text from documents.
    - When the document is a scanned image, OCR (Optical Character Recognition) is applied to extract text. Current implementations are Pytesseract, EasyOCR and TesserOCR.
    - When the document is a text-based document, the text is extracted directly. PdfMiner is used to extract elements from PDF.
- The **structured data extraction** is the process of extracting specific data from the extracted text.
    - The LLM is used to understand the context and extract data. The LLM can be with tooling integration or a standalone model (comming soon).
    - The output data is validated using Pydantic with custom validators

### 🏗️ Structure
Bellow is the structure of the project
- `config/`: Contains the configuration files (e.g., model schema, cost mapping, etc.)
- `data/`: Contains the data files (e.g., examples, documents, etc.)
- `cli/`: Contains all cli ui related files
- `core/`: Contains the core logic of the project
    - `cache_manager.py`: Caching for OCR results
    - `model_factory.py`: Dynamic pydantic model creation
    - `models.py`: Custom models to use as schema
    - `monitoring.py`: Monitoring of LLM usage
    - `validators.py`: Implementation of built-in validators for json schema
- `file_processor/`: Implementations of content extraction (e.g., unstructured, easyocr, etc.)
- `data_extractor/`: Implementations of structured data extraction (e.g., LLM, etc.)
- `.env`: Configuration file
- `requirements.txt`: Dependencies list files

### 📖 Full documentation ... (stay tuned)

## 🤝 Contribution
Feel free to contribute or to request features. You can open an issue or submit a pull request.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
> The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.