"""兼容入口；读取当前统一参数，禁止回写旧节奏。"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("merge_current_selections.py")),run_name="__main__")
