import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Type
from io import StringIO
import fnmatch
import os
from pdf2image import convert_from_path
import tempfile
import importlib
import pkgutil

JSON_IDENTATION = 2
FILE_ENCODING = "utf-8"


def load_json_file(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def ensure_dir_exists(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, encoding: str = FILE_ENCODING) -> None:
    ensure_dir_exists(path)
    with open(path, "wb") as f:
        f.write(content.encode(encoding))


def append_file(path: Path, content: str, encoding: str = FILE_ENCODING) -> None:
    ensure_dir_exists(path)
    with open(path, "a", encoding=encoding) as f:
        f.write(content)


def load_json_array(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding=FILE_ENCODING) as f:
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
    if not ("*" in pattern or "?" in pattern):
        return [Path(pattern)] if os.path.exists(pattern) else []

    base_dir = os.path.dirname(pattern) or "."
    file_pattern = os.path.basename(pattern)

    matching_files = []
    for root, _, files in os.walk(base_dir):
        for filename in files:
            if fnmatch.fnmatch(filename, file_pattern):
                matching_files.append(Path(os.path.join(root, filename)))

    return sorted(matching_files)


def update_monitoring_entry(
    existing_entry: Dict[str, Any], new_data: Dict[str, Any]
) -> None:
    for key in [
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "duration_seconds",
        "estimated_cost_usd",
    ]:
        existing_entry[key] += new_data[key]
    existing_entry["timestamp"] = new_data["timestamp"]


def find_monitoring_entry(
    data: List[Dict[str, Any]], model: str, provider: str
) -> Dict[str, Any] | None:
    return next(
        (
            entry
            for entry in data
            if entry["model"] == model and entry["provider"] == provider
        ),
        None,
    )


def write_monitoring_data(path: Path, new_data: Dict[str, Any]) -> None:
    if path.exists():
        existing_data = load_json_array(path)
        entry = find_monitoring_entry(
            existing_data, new_data["model"], new_data["provider"]
        )

        if entry:
            update_monitoring_entry(entry, new_data)
            content = json.dumps(
                existing_data, indent=JSON_IDENTATION, ensure_ascii=False
            )
            write_file(path, content)
        else:
            write_json(path, new_data)
    else:
        write_json(path, new_data)
