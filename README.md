# Document Information Extractor

A CLI tool to extract structured information from documents using Language Models.

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python cli.py document.pdf
```

### Command-line Options

#### Input Configuration
- `input_file`: Path to the document file (PDF, DOCX, TXT)
- `--languages`: List of languages to process (default: fr)
- `--strategy`: Processing strategy (fast/accurate, default: fast)

#### LLM Configuration
- `--model`: LLM model name (default: gemini-1.5-pro)
- `--provider`: LLM provider (default: google-genai)
- `--temperature`: Model temperature (default: 0.1)

#### Model Configuration
- `--examples`: Path to examples JSON file
- `--model-schema`: Path to model schema JSON file

### Examples

Process a French contract with accurate strategy:
```bash
python cli.py contract.pdf --strategy accurate
```

Use a different LLM model:
```bash
python cli.py contract.pdf --model gpt-4 --provider openai --temperature 0.2
```

Process multilingual document:
```bash
python cli.py contract.pdf --languages fr en de
```

## Output

The tool outputs extracted information in JSON format following the schema defined in the model configuration file.

## Configuration Files

- Examples: `data/examples.json`
- Schema: `config/leasing_model.json`

## License

MIT
