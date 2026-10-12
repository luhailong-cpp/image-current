"""Current delivery generator; preserves historical user acceptance."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('write_current_delivery.py')),run_name='__main__')
