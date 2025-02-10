import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Type
from io import StringIO
import fnmatch
import os
from PIL import Image
from pdf2image import convert_from_path
import tempfile
import importlib
import pkgutil

JSON_IDENTATION = 2
FILE_ENCODING = 'utf-8'

def load_json_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def ensure_dir_exists(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def write_file(path: Path, content: str, encoding: str = FILE_ENCODING) -> None:
    ensure_dir_exists(path)
    with open(path, 'wb') as f:
        f.write(content.encode(encoding))

def append_file(path: Path, content: str, encoding: str = FILE_ENCODING) -> None:
    ensure_dir_exists(path)
    with open(path, 'a', encoding=encoding) as f:
        f.write(content)

def load_json_array(path: Path) -> List[Dict[str, Any]]:
    with open(path, 'r', encoding=FILE_ENCODING) as f:
        data = json.load(f)
        return data if isinstance(data, list) else [data]

def write_json(path: Path, data: Dict[str, Any]) -> None:
    if path.exists():
        existing_data = load_json_array(path)
        existing_data.append(data)
        content = json.dumps(existing_data, indent=JSON_IDENTATION, ensure_ascii=False)
    else:
        content = json.dumps([data], indent=JSON_IDENTATION, ensure_ascii=False)
    write_file(path, content)

def write_csv_headers(path: Path, headers: List[str]) -> None:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    write_file(path, output.getvalue())

def append_csv_row(path: Path, row: List[str]) -> None:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(row)
    append_file(path, output.getvalue())

def write_csv(path: Path, data: Dict[str, str]) -> None:
    if not path.exists():
        write_csv_headers(path, list(data.keys()))
    append_csv_row(path, list(data.values()))

def find_files(pattern: str) -> List[Path]:
    if not ('*' in pattern or '?' in pattern):
        return [Path(pattern)] if os.path.exists(pattern) else []
    
    base_dir = os.path.dirname(pattern) or '.'
    file_pattern = os.path.basename(pattern)
    
    matching_files = []
    for root, _, files in os.walk(base_dir):
        for filename in files:
            if fnmatch.fnmatch(filename, file_pattern):
                matching_files.append(Path(os.path.join(root, filename)))
    
    return sorted(matching_files)

def update_monitoring_entry(existing_entry: Dict[str, Any], new_data: Dict[str, Any]) -> None:
    for key in ['input_tokens', 'output_tokens', 'total_tokens', 'duration_seconds', 'estimated_cost_usd']:
        existing_entry[key] += new_data[key]
    existing_entry['timestamp'] = new_data['timestamp']

def find_monitoring_entry(data: List[Dict[str, Any]], model: str, provider: str) -> Dict[str, Any] | None:
    return next(
        (entry for entry in data if entry['model'] == model and entry['provider'] == provider),
        None
    )

def write_monitoring_data(path: Path, new_data: Dict[str, Any]) -> None:
    if path.exists():
        existing_data = load_json_array(path)
        entry = find_monitoring_entry(existing_data, new_data['model'], new_data['provider'])
        
        if entry:
            update_monitoring_entry(entry, new_data)
            content = json.dumps(existing_data, indent=JSON_IDENTATION, ensure_ascii=False)
            write_file(path, content)
        else:
            write_json(path, new_data)
    else:
        write_json(path, new_data)

def convert_pdf_to_images(pdf_path: str) -> List[str]:
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    
    pages = convert_from_path(pdf_path)
    for i, page in enumerate(pages):
        image_path = os.path.join(temp_dir, f'page_{i}.png')
        page.save(image_path, 'PNG')
        image_paths.append(image_path)
    
    return image_paths

def handle_document_images_or_texts(file_path: str, image_handler_func) -> List[Any]:
    file_path = Path(file_path)
    results = []
    
    if file_path.suffix.lower() == '.pdf':
        temp_dir = tempfile.mkdtemp()
        try:
            image_paths = convert_pdf_to_images(str(file_path))
            for image_path in image_paths:
                result = image_handler_func(image_path)
                results.append(result)
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    else:
        results.append(image_handler_func(str(file_path)))
    
    return results

def is_macos() -> bool:
    return os.uname().sysname == 'Darwin'

def _is_valid_class_to_load(attr: Any, base_class: Type, exclude_base: bool) -> bool:
    if not isinstance(attr, type):
        return False
    if not issubclass(attr, base_class):
        return False
    if exclude_base and attr == base_class:
        return False
    return True

def load_classes_from_package(
    package_name: str,
    base_class: Type,
    module_suffix: str = '',
    exclude_base: bool = True
) -> Dict[str, Type]:
    classes = {}
    package = importlib.import_module(package_name)
    
    for _, name, _ in pkgutil.iter_modules(package.__path__):
        if module_suffix and not name.endswith(module_suffix):
            continue
            
        module = importlib.import_module(f'{package_name}.{name}')
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if _is_valid_class_to_load(attr, base_class, exclude_base):
                key = name.replace(module_suffix, '') if module_suffix else name
                classes[key] = attr
    
    return classes
