"""Compatibility loader for the legacy architect implementation.

The preserved implementation contains Python 3.11-incompatible f-string
expressions. Keep the implementation intact and normalize those syntax
patterns at load time so existing imports retain the same public API.
"""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import sys

_SOURCE = Path(__file__).with_name("architect_source.py")


class _CompatibilityLoader(SourceFileLoader):
    def get_data(self, path):
        text = super().get_data(path).decode("utf-8")
        replacements = {
            'print(f"\\n{\'\\u2500\'*70}\\nREQUIRED SKILLS (sorted by score \\u2193):")':
                'separator = "─" * 70\n    print(f"\\n{separator}\\nREQUIRED SKILLS (sorted by score ↓):")',
            'print(f"\\n{\'\\u2500\'*70}\\nMISMATCH REPORT ({len(mm)} fields differ stored vs derived):")':
                'separator = "─" * 70\n        print(f"\\n{separator}\\nMISMATCH REPORT ({len(mm)} fields differ stored vs derived):")',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode("utf-8")


_loader = _CompatibilityLoader(__name__, str(_SOURCE))
_spec = spec_from_loader(__name__, _loader)
_module = module_from_spec(_spec)
sys.modules[__name__] = _module
_loader.exec_module(_module)
globals().update(_module.__dict__)
