"""Refresh current N paired-ground evidence; historical four-contact phases are superseded."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('write_n_paired_ground_review.py')),run_name='__main__')
