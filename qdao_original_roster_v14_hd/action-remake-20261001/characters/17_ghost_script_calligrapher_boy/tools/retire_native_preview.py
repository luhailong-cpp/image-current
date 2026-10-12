"""Retire stale native/source preview entry points after final delivery is complete."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1]
m=json.loads((B/'manifest.json').read_text(encoding='utf-8'))
assert m['status']=='passed'
from plan_final_cleanup import validate_delivery
frames={f['slot']:f for s in m['sequences'] for f in s['frames']}
validate_delivery(frames,{(B/f['file']).resolve() for f in frames.values()})
changed=[]
for p in (B/'preview').glob('*.html'):
    if p.name=='delivery.html':continue
    p.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=delivery.html"><title>灵篆书生正式预览</title><p>制作预览已归档。<a href="delivery.html">打开完整动作成品</a></p></html>',encoding='utf-8')
    changed.append(p.name)
(B/'review/preview-entry-retirement.json').write_text(json.dumps({'redirectedTo':'preview/delivery.html','entries':changed,'selectionManifestRetained':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'retiredEntryCount':len(changed),'redirectedTo':'delivery.html'}))
