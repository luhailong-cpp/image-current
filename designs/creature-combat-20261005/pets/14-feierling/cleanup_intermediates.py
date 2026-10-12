"""Remove superseded in-scope images only after the final delivery passes checks."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check=json.loads((ROOT/'QA/technical-validation.json').read_text(encoding='utf-8'))
visual=json.loads((ROOT/'QA/visual-review.json').read_text(encoding='utf-8'))
assert check['technicalChecksPassed'] and visual['completed']
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
assert len(manifest['frames'])==68
for f in manifest['frames']:
 p=(ROOT/f['file']).resolve();assert p.is_relative_to(ROOT) and sha(p)==f['sha256']
 assert (ROOT/f['generationRecord']).is_file()
targets=[]
for p in (ROOT/'generation').rglob('*'):
 if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp']:targets.append(p.resolve())
for folder in [ROOT/'QA/attack',ROOT/'QA/cast-E']:
 if folder.exists():
  targets.extend(p.resolve() for p in folder.rglob('*') if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.html'])
for p in targets:
 assert p.is_relative_to(ROOT) and not p.is_relative_to(ROOT/'runtime'),str(p)
deleted=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'reason':'AI native/rejected/intermediate or superseded pre-export contact image; final PNG and text evidence retained'} for p in targets]
deleted_paths={str(p).lower() for p in targets}
for rp in (ROOT/'generation').rglob('*.generation.json'):
 r=json.loads(rp.read_text(encoding='utf-8-sig'))
 r['retention']={'policy':'Final game frames and current supporting files only; no project image backups. Prompts, receipts, historical paths and source SHA retained.','nativePixels':'not part of delivery; local intermediate removed after verified final export','externalSourceCache':'host-generated cache is outside the exclusive write scope and is not a required delivery dependency','submittedReferencePaths':'historical generation inputs; original shared identity/style files remain current and read-only'}
 for ref in r.get('references',[]):
  raw=ref.get('path') or ref.get('file')
  if not raw:continue
  p=Path(raw);p=p if p.is_absolute() else ROOT/p
  if str(p.resolve()).lower() in deleted_paths:
   ref['historicalOnly']=True;ref['retentionStatus']='intermediate pixels removed; text and recorded SHA retained'
  elif 'generated_images' in str(p).lower():
   ref['historicalOnly']=True;ref['retentionStatus']='historical model input; host cache outside task write scope, not a delivery dependency'
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
for p in targets:p.unlink()
(ROOT/'QA/cleanup.json').write_text(json.dumps({'completedAt':datetime.now(timezone.utc).isoformat(),'exclusiveRoot':str(ROOT),'removedCount':len(deleted),'removed':deleted,'sharedSourcesDeleted':False,'runtimeFramesRetained':68},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'removed':len(deleted),'runtimeRetained':68}))
