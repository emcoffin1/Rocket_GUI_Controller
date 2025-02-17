import os, sys, json
from pathlib import Path

def load_file(file:str, as_json=True):
    """Loads only the config"""
    try:
        # Get the file path
        file = get_file_path(file)
        with open(file, "r") as f:
            return json.load(f) if as_json else f.read()

    except Exception as e:
        print(f"ERROR: {e}")


def get_file_path(file:str) -> Path:
    """Gets the absolute path to ANY data file"""
    # Check if it's running as an exe
    if getattr(sys, "frozen", False):   # Directory of exe
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent.parent    # Directory of script
    return base_dir/file
