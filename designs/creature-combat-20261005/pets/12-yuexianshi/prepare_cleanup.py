"""Prepare an exact hash-verified native-image cleanup list for this task only."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CACHE=Path('C:/Users/luyua/.codex/generated_images').resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items={}
def add(path,digest,record):
    if not path or not digest:return
    p=Path(path).resolve()
    if not p.is_relative_to(CACHE) or p.suffix.lower()!='.png':return
    key=str(p).lower()
    if key in items:
        assert items[key]['sha256']==digest
        items[key]['records'].append(record)
    else:items[key]={'path':str(p),'sha256':digest,'records':[record]}
for p in (ROOT/'records').rglob('*.generation.json'):
    r=json.loads(p.read_text(encoding='utf-8-sig'));rel=p.relative_to(ROOT).as_posix()
    d=r.get('derivedFrom',{});add(d.get('path'),d.get('sha256'),rel)
    add(r.get('file'),r.get('sha256'),rel)
for item in items.values():
    p=Path(item['path']);item['exists']=p.exists()
    if p.exists():assert sha(p)==item['sha256'],str(p)
plan={'reason':'2026-09-23 user retention policy: final sprites and supporting deliverables only; keep generation text and hashes, remove own original/rejected/intermediate images after final references checked.','cacheRoot':str(CACHE),'count':len(items),'items':list(items.values())}
(ROOT/'cleanup-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'plannedNativeFiles':len(items),'existing':sum(x['exists'] for x in items.values()),'action':'plan only, no files deleted'}))
