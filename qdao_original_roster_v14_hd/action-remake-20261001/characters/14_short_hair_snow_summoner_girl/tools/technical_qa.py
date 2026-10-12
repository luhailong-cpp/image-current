"""Read-only QA of delivery images/provenance; no inferred visual approval."""
from pathlib import Path
import hashlib,json
from collections import defaultdict
from datetime import datetime,timezone
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1]
SPECS={'run':(['N','NE','E','SE','S','SW','W','NW'],16),'hit':(['E','W'],6),'attack':(['E','W'],12),'cast':(['E','W'],16)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(p):
 q=Path(p)
 return q if q.is_absolute() else R/q
rows=[]; hashes=defaultdict(list); natives=defaultdict(list)
for action,(dirs,count) in SPECS.items():
 for direction in dirs:
  for n in range(1,count+1):
   slot=f'{action}/{direction}/{n:02d}';p=R/(slot+'.png');errors=[]
   if not p.exists():
    rows.append({'slot':slot,'errors':['missing_frame']});continue
   h=sha(p);hashes[h].append(slot)
   im=Image.open(p);meta=Path(str(p)+'.generation.json')
   if im.size!=(1024,1024) or im.mode!='RGBA':errors.append('invalid_export_format')
   a=np.array(im.getchannel('A'));bbox=im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()
   if int(a.min())!=0 or int(a.max())!=255:errors.append('unexpected_alpha')
   if max(int(a[0,:].max()),int(a[-1,:].max()),int(a[:,0].max()),int(a[:,-1].max()))>8:errors.append('opaque_pixels_touch_canvas')
   rec=json.loads(meta.read_text(encoding='utf-8-sig')) if meta.exists() else {}
   if rec.get('sha256')!=h:errors.append('generation_record_sha_mismatch')
   origin=rec.get('derivedFrom',{});source=resolve(origin.get('file',origin.get('path','_missing')))
   nh=origin.get('sha256');natives[nh].append(slot)
   nr=resolve(origin.get('generationRecord','_missing'))
   native=json.loads(nr.read_text(encoding='utf-8-sig')) if nr.exists() else {}
   if not nr.exists():errors.append('native_record_missing')
   if native.get('sha256')!=nh:errors.append('native_record_sha_mismatch')
   if min(origin.get('nativeSize',[0,0]))<1024:errors.append('native_resolution_below_1024')
   if source.exists() and sha(source)!=nh:errors.append('native_sha_mismatch')
   if not source.exists() and not origin.get('bitmapRemovedAfterFinalVerification'):errors.append('native_file_missing_without_retention_record')
   reg=rec.get('registrationTransform',{})
   direct=(reg.get('method')=='direct_registered_canvas_redraw' and reg.get('globalScale')==1.0 and reg.get('inheritedCharacterScale')==.8 and reg.get('sourceRoot')==[512,942])
   standard=(reg.get('globalScale')==.8 and reg.get('method')!='direct_registered_canvas_redraw')
   if reg.get('outputSha256')!=h or not (standard or direct) or reg.get('targetRoot')!=[512,942]:errors.append('registration_pending_or_invalid')
   rows.append({'slot':slot,'sha256':h,'nativeSha256':nh,'alphaBoundsAbove8':bbox,'generationRecord':meta.relative_to(R).as_posix(),'nativeRecord':str(nr),'errors':errors})
duplicate=[v for v in hashes.values() if len(v)>1]
duplicateNative=[v for v in natives.values() if len(v)>1]
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'expected':196,'present':sum('sha256' in r for r in rows),'technicalPass':sum(not r['errors'] for r in rows),'duplicateExports':duplicate,'duplicateNativeSources':duplicateNative,'visualApprovalImplied':False,'clientValidated':False,'frames':rows}
(R/'audit/technical-qa.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='frames'},ensure_ascii=False))
print(json.dumps({'problems':[{'slot':r['slot'],'errors':r['errors']} for r in rows if r['errors']]},ensure_ascii=False))

