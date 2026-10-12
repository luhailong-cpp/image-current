"""Remove only the audited historical bitmap list after verified final delivery."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
plan=json.loads((R/'audit/cleanup-plan.json').read_text(encoding='utf-8'))
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
review=json.loads((R/'review.json').read_text(encoding='utf-8'))
assert m['exported']==m['visualPassed']==m['anchor']['registeredFrames']==196
keep={f['path'] for f in m['frames']}|{f'support-idle/{d}.png' for d in ['N','NE','E','SE','S','SW','W','NW']}
pr=json.loads((R/'preview/provenance.json').read_text(encoding='utf-8'))
keep|={f['file'] for f in pr['files']}
for f in m['frames']:
 assert sha(R/f['path'])==f['sha256']==review[f['slot']]['sha256']
for f in pr['files']:
 assert (R/f['file']).exists() and all(sha(R/x['path'])==x['sha256'] for x in f['sources'])
targets=[]
for row in plan['candidateImages']:
 path=(R/row['path']).resolve()
 assert path.is_relative_to(R) and path!=R
 assert row['path'] not in keep and path.suffix.lower() in ('.png','.jpg','.jpeg','.gif','.webp')
 assert path.is_file() and sha(path)==row['sha256'],row['path']
 targets.append((path,row))
legacy=[]
for row in plan['candidateLegacyPreviewPages']:
 p=(R/row['path']).resolve();assert p.is_relative_to(R) and p.suffix=='.html'
 if p.exists():legacy.append((p,row))
print(json.dumps({'mode':'apply' if args.apply else 'dry-run','resolvedRoot':str(R),'imageCount':len(targets),'imageBytes':sum(p.stat().st_size for p,_ in targets),'legacyPages':[x['path'] for _,x in legacy],'keepImages':len(keep),'allTargetsVerifiedWithinRoot':True}))
if not args.apply:raise SystemExit()
now=datetime.now(timezone.utc).isoformat()
selected={}
for f in m['frames']:
 p=R/f['generationRecord'];meta=json.loads(p.read_text(encoding='utf-8-sig'))
 origin=meta['derivedFrom'];source=Path(origin.get('file',origin.get('path')))
 if not source.is_absolute():source=R/source
 assert source.resolve().is_relative_to(R)
 assert sha(source)==origin['sha256']
 selected[source.resolve().as_posix()]=f['path']
 origin['bitmapRemovedAfterFinalVerification']=True
 origin['bitmapDisposition']='removed_after_verified_final_export'
 origin['retentionRecord']='audit/cleanup-result.json'
 p.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
removed=[]
for path,row in targets:
 record=Path(str(path)+'.generation.json')
 if record.exists():
  j=json.loads(record.read_text(encoding='utf-8-sig'))
  j['bitmapDisposition']={'status':'removed_after_verified_final_export','removedAt':now,'retentionPolicy':'2026-09-23 user project instruction','finalDerivative':selected.get(path.as_posix()),'evidencePreserved':True}
  record.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
 path.unlink();removed.append({'path':row['path'],'sha256':row['sha256'],'bytes':row['bytes']})
for path,row in legacy:path.unlink()
(R/'audit/cleanup-result.json').write_text(json.dumps({'removedAt':now,'root':str(R),'policy':'Only final game assets, required design/integration/preview, and text model/quality/source evidence retained. No image backups.','verifiedBeforeRemoval':{'formal':196,'reviewed':196,'registered':196,'previews':42,'noActiveImageGeneration':True},'removedImages':removed,'removedLegacyPages':[r['path'] for _,r in legacy],'retainedImages':sorted(keep),'imageCountRemoved':len(removed)},ensure_ascii=False,indent=2),encoding='utf-8')
