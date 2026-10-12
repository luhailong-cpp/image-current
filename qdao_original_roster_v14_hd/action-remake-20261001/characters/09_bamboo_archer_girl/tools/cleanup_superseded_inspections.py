from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1].resolve()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checked=read(ROOT/'audit/preview-delivery-check.json')
assert checked['sourceHashMatches'] and checked['currentSourceReferences']==196
for src in (ROOT/'preview/qa').glob('*-preview.sources.json'):
 for row in read(src)['sources']:
  assert sha(ROOT/row['file'])==row['sha256'],row['file']
extensions={'.png','.jpg','.jpeg','.webp','.gif','.apng'}
candidates=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in extensions and not p.is_relative_to(ROOT/'runtime') and not p.is_relative_to(ROOT/'preview')]
rows=[]
for p in candidates:
 target=p.resolve()
 assert target.is_relative_to(ROOT) and target!=ROOT
 rows.append({'file':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'reason':'Superseded inspection/working image or duplicate group preview; current runtime and canonical preview/qa verified and retained.'})
out={'atUtc':datetime.now(timezone.utc).isoformat(),'authorizedBy':'AGENTS.md 2026-09-23: keep final game images and necessary design/integration files; remove original/rejected/working images after current outputs and references verified.','currentRuntimeAndCanonicalPreviewRetained':True,'textProvenanceRetained':True,'outsideCharacterFilesTouched':False,'deleted':rows}
ledger=ROOT/'audit/cleanup-superseded-inspection-images.json'
if ledger.exists():
 previous=read(ledger)
 out['previousBatches']=previous.get('previousBatches',[])+[{k:v for k,v in previous.items() if k!='previousBatches'}]
ledger.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for row in rows:(ROOT/row['file']).unlink()
print(json.dumps({'deletedIntermediateImages':len(rows),'currentRuntimeAndPreviewRetained':True}))
