from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inv=json.loads((R/'candidate-inventory.json').read_text(encoding='utf-8-sig'))
orders=json.loads((R/'run-playback-proposals.json').read_text(encoding='utf-8-sig'))['groups']
runreg=json.loads((R/'candidate/registration.json').read_text(encoding='utf-8-sig'))
battlereg=json.loads((R/'candidate/battle-registration.json').read_text(encoding='utf-8-sig'))
groups={};allrows=[];sums=[]
for group,frames in inv['groups'].items():
 action,direction=group.split('/')
 expected={'run':16,'hit':6,'attack':12,'cast':16}[action]
 if len(frames)!=expected or {f['frame'] for f in frames}!=set(range(1,expected+1)):raise ValueError('Incomplete '+group)
 order=orders.get(group,list(range(1,expected+1))) if action=='run' else list(range(1,expected+1))
 if sorted(order)!=list(range(1,expected+1)):raise ValueError('Invalid order '+group)
 translation=(runreg['directions'][direction] if action=='run' else battlereg['groups'][group])['translation']
 rows=[]
 for playframe,sourceframe in enumerate(order,1):
  f=next(f for f in frames if f['frame']==sourceframe);src=R/f['url'][3:]
  if sha(src)!=f['sha256']:raise ValueError('Stale source '+str(src))
  im=Image.open(src);im.load()
  if im.mode!='RGBA' or im.size!=(1254,1254):raise ValueError('Bad native '+str(src))
  nativerecord=Path(str(src)+'.generation.json')
  if not nativerecord.exists():raise ValueError('Missing provenance '+str(src))
  out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((860,860),Image.Resampling.LANCZOS),tuple(translation))
  dest=R/'runtime'/group/f'{playframe:02}.png';dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
  metadata={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'width':1024,'height':1024,'mode':'RGBA','exportedAt':datetime.now(timezone.utc).isoformat(),'operation':'same1254-to860 whole-canvas scale plus one fixed translation per direction/action; no per-frame grounding, mirroring, interpolation or copied pose','translation':translation,'nativeEvidence':{'historicalFile':src.relative_to(R).as_posix(),'sha256':sha(src),'size':[1254,1254],'mode':'RGBA','generationRecord':nativerecord.relative_to(R).as_posix(),'recordSHA256':sha(nativerecord)},'actualModel':None,'actualQuality':None,'unverifiedReason':'builtin image tool exposes no model/quality selector or verified result values','sourceFrame':sourceframe,'playbackFrame':playframe,'frameDurationMs':{'run':75,'hit':40,'attack':30,'cast':45}[action],'clientIntegrated':False}
  write(Path(str(dest)+'.generation.json'),metadata)
  row={'frame':playframe,'sourceFrame':sourceframe,'url':'../'+dest.relative_to(R).as_posix(),'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'nativeSHA':sha(src),'nativeSize':[1254,1254],'nativeSource':src.relative_to(R).as_posix(),'generationRecord':str(dest.relative_to(R))+'.generation.json','durationMs':metadata['frameDurationMs']}
  if action=='attack' and playframe==6:row['event']='contact'
  if action=='cast' and playframe==9:row['event']='release'
  rows.append(row);allrows.append({'group':group,**row});sums.append(sha(dest)+'  '+dest.relative_to(R).as_posix())
 groups[group]=rows
if len(allrows)!=196 or len({x['sha256'] for x in allrows})!=196:raise ValueError('Count or duplicate export failed')
delivery={'character':'10_crimson_spear_girl','status':'current-art-production-export','updatedAt':datetime.now(timezone.utc).isoformat(),'producedNative':196,'runtimeCount':196,'runFrameMs':75,'runCycleMs':1200,'phaseWeightsApplied':False,'orders':{},'groups':groups,'clientIntegrated':False,'clientRuntimeTested':False,'sourceOrderNote':'Runtime01..16 already follows reviewed playback order; native sourceFrame is retained for provenance. Do not apply old source order again.'}
write(R/'delivery-current.json',delivery)
(R/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n',encoding='utf-8')
write(R/'runtime-export-report.json',{'count':196,'uniqueSHA':196,'nativeEvidenceVerified':196,'canvas':[1024,1024],'mode':'RGBA','root':[512,942],'runFrameMs':75,'cycleMs':1200,'uniform':True,'sourceOrderAppliedOnce':True,'clientIntegrated':False})
print(json.dumps({'runtimeCount':196,'runCycleMs':1200,'runFrameMs':75,'sourceOrderAppliedOnce':True}))

