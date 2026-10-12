import sys
sys.dont_write_bytecode=True
import importlib.util
from pathlib import Path
Z=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location('c07_local_prod',Z/'production.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
orig=p.write
p.write=lambda path,obj: None if path.name=='progress.json' else orig(path,obj)
if sys.argv[1]=='prepare':
 stem='_'.join(sys.argv[2:]);assert not (Z/'native'/(stem+'.request.json')).exists(), 'Existing request: inspect before retry'
 p.prepare(*sys.argv[2:])
elif sys.argv[1]=='record':p.record(sys.argv[2])
