"""Verify real native inputs, one-to-one export transforms, and provenance before retention cleanup."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];errors=[]
for p in sorted((R/'runtime').glob('*/*/*.png')):
 r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'))
 refs=r.get('derivedFrom',[])
 if len(refs)!=1:errors.append(str(p)+' source count');continue
 src=R/refs[0]['file'];sr=R/refs[0]['generationRecord'];g=json.loads(sr.read_text(encoding='utf-8-sig'))
 if not src.exists():
  # Earlier retention cleanup may already have removed project-native duplicates.
  # Read the exact recorded host receipt, if still available; never restore a backup.
  src=Path(g.get('evidence',{}).get('hostOutputPath',''))
  if not src.is_file():raise FileNotFoundError('No current native or recorded host receipt for '+str(p))
 with Image.open(src) as native:
  native.load();native=native.convert('RGBA');size=list(native.size)
  camera=r.get('cameraRegistration',{})
  if camera.get('applied'):
   assert camera['resampledSize']==[901,901] and camera['placement']==[61,97]
   expected=Image.new('RGBA',(1024,1024));expected.alpha_composite(native.resize((901,901),Image.Resampling.LANCZOS),(61,97))
  else:expected=native.resize((1024,1024),Image.Resampling.LANCZOS)
  actual=Image.open(p).convert('RGBA')
  exact=expected.tobytes()==actual.tobytes()
 row={'file':p.relative_to(R).as_posix(),'sha256':sha(p),'nativeFile':refs[0]['file'],'nativeReadPath':str(src),'nativeSha256':sha(src),'nativeActualDimensions':size,'nativeRecord':refs[0]['generationRecord'],'nativeShaMatches':sha(src)==refs[0]['sha256']==g['sha256'],'runtimeShaMatches':sha(p)==r['sha256'],'exactDeclaredTransformPixels':exact,'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),'alphaExtrema':list(actual.getchannel('A').getextrema())}
 rows.append(row)
 if min(size)<1024 or not row['nativeShaMatches'] or not row['runtimeShaMatches'] or not exact:errors.append(row['file'])
unique=len({r['nativeSha256'] for r in rows})
if len(rows)!=196 or unique!=196:errors.append('expected196 unique native sources')
out={'verifiedAt':datetime.now(timezone.utc).isoformat(),'runtimeFrames':len(rows),'uniqueNativeSources':unique,'errors':errors,'passed':not errors,'method':'Actual native PNG decode and SHA; regenerate declared full-canvas transform in memory and compare every RGBA byte to runtime. No files changed except this JSON.','records':rows,'retentionNote':'This evidence records actual native presence before optional deletion per user retention policy; original text generation records remain.'}
(R/'review/native_export_verification_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(rows),'uniqueSources':unique,'passed':not errors,'errors':errors}))
raise SystemExit(bool(errors))
