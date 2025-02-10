import os
import time
import sys
from typing import List
from dotenv import load_dotenv
from data_extractor.llm_extractor import LLMDataExtractor
from file_processor.unstructured_processor import UnstructuredFileProcessor
from core.model_factory import ModelFactory
import json

load_dotenv()
LANGUAGES: List[str] = os.getenv("LANGUAGES", "fr").split(",")
PDF_STRATEGY: str = os.getenv("PDF_STRATEGY", "auto")
CACHE_DIR: str = os.getenv("CACHE_DIR", "./tmp/cache")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <file_path> <model_config_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    model_json_path = sys.argv[2]
    
    file_processor = UnstructuredFileProcessor(file_path=file_path, languages=LANGUAGES, strategy=PDF_STRATEGY)
    
    start_time = time.time()
    full_content = file_processor.get_text_content()
    print(f"Time to process file: {time.time() - start_time} seconds")


    extractor = LLMDataExtractor()
    model_config = ModelFactory.load_model_json_file(model_json_path)
    DynamicModel = ModelFactory.create_model(model_config)
    
    start_time = time.time()
    extractor.load_examples_json_file("data/examples.json")
    result = extractor.extract(full_content, DynamicModel)
    print(result)
    print(f"Time to extract: {time.time() - start_time} seconds")
