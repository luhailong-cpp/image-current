from pathlib import Path
import importlib.util,sys,json
T=Path(__file__).resolve().parent.parent/'r07_c13'
spec=importlib.util.spec_from_file_location('production',T.parent/'production.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.TILE=T;p.update=lambda *a,**k:None
orig=p.save
def save(path,data):
 path=Path(path).resolve()
 if not path.is_relative_to(T.resolve()) or not path.name.startswith('p24'):raise RuntimeError('Only delegated p24 writes are allowed: '+str(path))
 orig(path,data)
p.save=save
if sys.argv[1]=='context':
 for tile,patch,box,pos in p.context_neighbors('p24'):
  src=p.selected_native(tile,patch);side=Path(str(src)+'.generation.json')
  if not src.is_file() or not side.is_file():raise RuntimeError('Required real neighbor missing: '+str(src))
  if json.loads(side.read_text(encoding='utf-8-sig'))['sha256']!=p.sha(src):raise RuntimeError('Neighbor SHA mismatch')
 p.context('p24')
elif sys.argv[1]=='ingest':p.ingest('p24',sys.argv[2])
else:raise ValueError(sys.argv[1])
