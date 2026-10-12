from pathlib import Path
import runpy
# Full extension audit: all raw versions and both native repair replays.
runpy.run_path(str(Path(__file__).with_name('audit-extension-final.py')), run_name='__main__')
