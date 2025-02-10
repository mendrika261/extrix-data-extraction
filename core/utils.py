import json
from typing import Any, Dict


def load_json_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data
    