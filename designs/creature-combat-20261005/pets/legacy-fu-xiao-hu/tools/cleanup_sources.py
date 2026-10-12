"""Remove superseded local rasters only after final frame/source/review verification."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/'manifest.json');v=read(ROOT/'validation.json');s=read(ROOT/'records/source-audit.json');a=read(ROOT/'records/visual-review.json')
assert len(m['frames'])==68 and v['technicalPassed'] and s['passed'] and a['passed']
assert a['frameSHA256']=={f['file']:sha(ROOT/f['file']) for f in m['frames']}
removed=[]
candidates=list((ROOT/'runtime/cast/E/.native').glob('*.png'))+[ROOT/'records/cast-E-review-contact.png']
for p in candidates:
 p=p.resolve()
 assert p.is_relative_to(ROOT) and p.suffix.lower()=='.png'
 if not p.exists():continue
 removed.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'reason':'superseded native or intermediate QA raster; final 68 exports, source text, design references and preview verified'})
 p.unlink()
native=ROOT/'runtime/cast/E/.native'
if native.exists() and not any(native.iterdir()):native.rmdir()
report={'at':datetime.now(timezone.utc).isoformat(),'removed':removed,'retained':'68 runtime PNGs, current E/W design references, final shared preview assets and all textual generation evidence','outsideScope':'Original shared identity/style references and host generated_images caches were not modified; host caches are not runtime dependencies'}
(ROOT/'records/final-cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'removed':len(removed)}))
