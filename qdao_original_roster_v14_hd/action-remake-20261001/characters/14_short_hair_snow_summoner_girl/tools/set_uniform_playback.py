"""Compatibility entry point; preserve the current timing unless --frame-ms is supplied."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("set_current_timing.py")), run_name="__main__")
