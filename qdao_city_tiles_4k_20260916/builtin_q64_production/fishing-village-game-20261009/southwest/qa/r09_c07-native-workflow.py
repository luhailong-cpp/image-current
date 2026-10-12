from pathlib import Path
import json,sys,importlib.util
z=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scoped_production',z/'production.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def scoped_write(path,obj):
 path=Path(path)
 if path.name=='progress.json': return
 assert path.parent in [z/'native',z/'layout-only'] and path.name.startswith('r09_c07'),str(path)
 path.parent.mkdir(exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p.write=scoped_write
cmd=sys.argv[1]
if cmd=='prepare':
 patch=sys.argv[2];ver=sys.argv[3] if len(sys.argv)>3 else 'v1'
 p.prepare('r09_c07',patch,ver)
 stem=f'r09_c07_{patch}_{ver}'
 rpath=z/'native'/f'{stem}.request.json'
 d=json.loads(rpath.read_text());d['references']=d['references'][:4]
 for ref in d['references']:ref['sha256']=p.sha(ref['path'])
 scoped_write(rpath,d)
elif cmd=='record':
 assert sys.argv[2].startswith('r09_c07_')
 p.record(sys.argv[2])
else:raise ValueError(cmd)

