"""Verify deliverable references and hashes after cleanup, without native-image dependency."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(raw):
 p=Path(raw);return p if p.is_absolute() else ROOT/p
m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));issues=[];rows=[]
assert len(m['frames'])==68
for f in m['frames']:
 p=ROOT/f['file'];r=json.loads((ROOT/f['generationRecord']).read_text(encoding='utf-8'))
 assert sha(p)==f['sha256']==r['sha256']
 assert resolve(r['prompt']).is_file()
 assert r['actualModel'] is None and r['actualQuality'] is None
 assert r['submittedParameters']['model'] is None and r['submittedParameters']['quality'] is None
 assert r['operation']['type']=='fixed-direction-export'
 assert r['operation']['perFrameAlignment'] is False
 for ref in r['references']:
  raw=ref.get('path') or ref.get('file')
  if ref.get('historicalOnly'):continue
  rp=resolve(raw)
  if not rp.exists():issues.append({'file':f['file'],'missingCurrentReference':raw})
  elif ref.get('sha256') and sha(rp)!=ref['sha256']:issues.append({'file':f['file'],'referenceHashMismatch':raw})
 with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=='RGBA'
 rows.append({'file':f['file'],'sha256':f['sha256']})
for doc in [ROOT/'README.md',ROOT/'MERGE_HANDOFF.md',ROOT/'STATUS.md']:
 for raw in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
  if raw.startswith(('http:','https:','#')):continue
  if (doc.parent/raw).resolve()==(ROOT/'QA/final-validation.json').resolve():continue
  if not (doc.parent/raw.split('#')[0]).exists():issues.append({'document':doc.name,'missingLink':raw})
current_images=list((ROOT/'runtime').rglob('*.png'))
assert len(current_images)==68
remaining_intermediates=[p.relative_to(ROOT).as_posix() for p in (ROOT/'generation').rglob('*') if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp']]
if remaining_intermediates:issues.append({'remainingGenerationImages':remaining_intermediates})
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'frameCount':68,'shaMatchesGenerationAndManifest':True,'currentReferencesChecked':True,'sourceImagesRequiredForPlayback':False,'remainingGenerationImages':len(remaining_intermediates),'issues':issues,'passed':not issues,'frames':rows,'clientValidated':False}
(ROOT/'QA/final-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False))
assert not issues
