import json
from pathlib import Path

from platformdirs import user_data_dir
from pydantic import ValidationError

from student_shuffle.models import History


def get_data_file_path():
    data_dir = Path(user_data_dir("Student Shuffle", "Lorenz Krötzsch"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "history.json"


def load_history():
    file_path = get_data_file_path()
    if not file_path.exists():
        return History()

    raw = file_path.read_text(encoding="utf-8")
    try:
        return History.model_validate_json(raw)
    except (ValidationError, ValueError, json.JSONDecodeError):
        decoded = json.loads(raw)
        if isinstance(decoded, str):
            return History.model_validate_json(decoded)
        return History.model_validate(decoded)


def save_history(history):
    file_path = get_data_file_path()
    file_path.write_text(history.model_dump_json(indent=4), encoding="utf-8")
