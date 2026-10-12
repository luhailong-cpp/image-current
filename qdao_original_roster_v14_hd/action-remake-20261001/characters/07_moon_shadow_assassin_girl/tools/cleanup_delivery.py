"""Prune intermediate pixels after final references and native evidence have passed."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from verify_manifest import verify
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=load(ROOT/'manifest.json')
assert m['formalAccepted'] and len(m['frames'])==196
report=verify(m,True)
assert report['passed'],report['errors']
save(ROOT/'review/pre-cleanup-structure-report.json',report)
keep={str((ROOT/f['path']).resolve()) for f in m['frames']}
keep.update(str((ROOT/a['path']).resolve()) for a in load(ROOT/'preview/derivations.json')['artifacts'])
remove=[]
for folder in ('staging','provenance','review','preview'):
 for path in (ROOT/folder).rglob('*'):
  if path.suffix.lower() not in ('.png','.jpg','.jpeg','.gif','.webp'):continue
  resolved=path.resolve()
  assert resolved.is_relative_to(ROOT) and resolved!=ROOT
  if str(resolved) in keep:continue
  remove.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size,'reason':'source/rejected/intermediate image; final game frame or required preview verified'})
ledger={'at':datetime.now(timezone.utc).isoformat(),'authorization':'AGENTS.md material-retention preference confirmed2026-09-23; only this character scope','removed':remove,'retainedGameFrames':196,'retainedPreviews':len(keep)-196,'historicalReferences':'Paths in old prompts, selections and generation evidence describe historical source pixels; current references are manifest.frames.path and preview/derivations.json only.'}
save(ROOT/'review/cleanup-ledger.json',ledger)
# Every destination has already been resolved and allowlisted; individual files only.
for item in remove:
 path=(ROOT/item['path']).resolve()
 assert path.is_relative_to(ROOT) and str(path) not in keep and sha(path)==item['sha256']
 path.unlink()
for f in m['frames']:
 f['nativeProvenance']['disposition']='removed_after_verified_export'
 np=ROOT/f['nativeProvenance']['generationRecord']
 rec=load(np);rec['assetDisposition']='source_removed_after_verified_export'
 rec['cleanupLedger']='review/cleanup-ledger.json';save(np,rec)
save(ROOT/'manifest.json',m)
final=verify(m,True)
save(ROOT/'preview/structure-report.json',final)
assert final['passed'],final['errors']
print(json.dumps({'removedImages':len(remove),'removedBytes':sum(x['bytes'] for x in remove),'gameFrames':196,'requiredPreviews':len(keep)-196,'verified':True}))

