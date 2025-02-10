import json
import csv
from pathlib import Path
from typing import Any, Dict, List
from io import StringIO

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
