# Compatibility entry point: the complete reviewed observations are maintained separately.
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_diagonal_preview.py')),run_name='__main__')

