"""Use standard source records; keep this worker's progress in an isolated file."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util
Q=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('c07_production',Q.parent/'production.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
original_write=p.write
def write(path,obj):
    if path.resolve()==(Q.parent/'progress.json').resolve():path=Q/'r09_c07-worker-progress.json'
    original_write(path,obj)
p.write=write
if sys.argv[1]=='record':p.record(sys.argv[2])
elif sys.argv[1]=='prepare':p.prepare(*sys.argv[2:])
else:raise ValueError('Only record/prepare permitted')
