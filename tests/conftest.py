"""Add tools/ directory to Python path and handle hyphenated module names."""

import importlib.util
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent / "tools"

# Map hyphenated filenames to importable module names
_HYPHEN_MODULES = {
    "i2i_signal": TOOLS_DIR / "i2i-signal.py",
    "i2i_review": TOOLS_DIR / "i2i-review.py",
    "i2i_resolve": TOOLS_DIR / "i2i-resolve.py",
    "i2i_messages": TOOLS_DIR / "i2i_messages.py",
}

for module_name, filepath in _HYPHEN_MODULES.items():
    if filepath.exists() and module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(module_name, str(filepath))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
