import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,importlib.util,re,hashlib
Z=Path(__file__).resolve().parent.parent
D=Z/'stair-rebuild'
s=importlib.util.spec_from_file_location('base_assembler',Z/'qa/full-tile-assemble.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
orig=m.select
def select(tile):
    out=orig(tile)
    pattern=re.compile(re.escape(tile)+r'_p(\d{2})_(\d{2})_v(\d+)\.png\.generation\.json$')
    for p in sorted(D.glob(tile+'_p*.png.generation.json')):
        x=pattern.fullmatch(p.name)
        if not x: continue
        r,c,v=map(int,x.groups());rec=m.read(p)
        if any(s in rec.get('status','') for s in ['rejected','superseded','frozen']):continue
        if (r,c) not in out or v>out[(r,c)][0]:out[(r,c)]=(v,p,rec)
    return out
m.select=select
m.QA=D
sys.argv=[__file__,'--tile','r10_c04']
m.main()
p=D/'full-tile-r10_c04-assembly.json'
j=m.read(p)
j['wrapper']={'path':Path(__file__).as_posix(),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'selection':'highest non-rejected numerical versions across historical native and stair-rebuild; no source mutated'}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
