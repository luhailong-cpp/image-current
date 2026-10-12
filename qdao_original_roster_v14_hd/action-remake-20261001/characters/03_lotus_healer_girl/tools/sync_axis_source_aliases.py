"""Synchronize source-review aliases after the guarded seven-frame selection."""
from pathlib import Path
import json
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=read(B/'review/axis-revision-decisions-20261004.json')
for item in plan['decisions']:
    path=B/f"review/run-{item['direction']}-sequence-input.json"
    data=read(path); f=data['frames'][item['frame']-1]
    assert (B/f['source']).resolve()==(B/item['source']).resolve()
    meta=read(B/(item['source']+'.generation.json'))
    if 'generationRecord' in f: f['generationRecord']=item['source']+'.generation.json'
    for key in ['nativeBoundsAlphaGt8','nativeAlphaGt8Bounds','alphaGt8Bounds']:
        if key in f: f[key]=meta['alphaGt8Bounds']
    for key in ['review','supportReview']:
        if key in f: f[key]=item.get('review',Path(item['source']).with_suffix('.selection-review.json').as_posix())
    write(path,data)
print('Synchronized seven selected sources and review aliases.')
