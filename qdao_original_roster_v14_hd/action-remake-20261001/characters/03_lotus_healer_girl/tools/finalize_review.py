"""Compatibility entry; current multi-action pipeline."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("finalize_actions_review.py")),run_name="__main__")
