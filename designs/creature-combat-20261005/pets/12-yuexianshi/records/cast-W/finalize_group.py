from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/12-yuexianshi')
rd=root/'records/cast-W'
for n in (5,6):
 p=rd/'attempts'/f'{n:02}-initial.generation.json'
 d=json.loads(p.read_text(encoding='utf-8'))
 d['prompt']=f'prompts/cast-W/{n:02}-initial.txt'
 d['evidence']['receipt']=f'records/cast-W/attempts/{n:02}-initial.receipt.json'
 d['status']='superseded: actual native right-ribbon clipping, repaired by builtin imagegen; original text evidence retained'
 d['supersededBy']=f'records/cast-W/{n:02}.generation.json'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 for kind in ('generation','job'):
  p=rd/f'{n:02}.{kind}.json'
  d=json.loads(p.read_text(encoding='utf-8'))
  d['references'][3]['role']='exact cast-W frame edit target: repair clipped right ribbon only'
  if len(d['references'])>4:d['references'][4]['role']='accepted repaired frame05 ribbon continuity reference'
  if kind=='generation':
   d['supersedes']=f'records/cast-W/attempts/{n:02}-initial.generation.json'
   d['visualStatus']='viewed: accepted surgical ribbon-edge repair, original pose and anatomical left support/right playing grip retained; native strong-alpha edges no longer clipped; playback pending'
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 p=rd/'attempts'/f'{n:02}-initial.job.json'
 d=json.loads(p.read_text(encoding='utf-8'))
 d['prompt']=f'prompts/cast-W/{n:02}-initial.txt'
 d['receipt']=f'records/cast-W/attempts/{n:02}-initial.receipt.json'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
frames=[]; hashes=[]
for n in range(1,17):
 p=root/'runtime/cast/W'/f'{n:02}.png'
 d=json.loads((rd/f'{n:02}.generation.json').read_text(encoding='utf-8'))
 im=Image.open(p)
 h=hashlib.sha256(p.read_bytes()).hexdigest();hashes.append(h)
 assert im.size==(1024,1024) and im.mode=='RGBA'
 assert im.getchannel('A').getextrema()==(0,255)
 assert h==d['sha256']
 assert (root/d['prompt']).is_file() and (root/d['evidence']['receipt']).is_file()
 for r in d['references']:
  rp=Path(r['path'])
  assert rp.is_file()
  assert hashlib.sha256(rp.read_bytes()).hexdigest()==r['sha256']
 frames.append({'frame':n,'file':d['file'],'record':f'records/cast-W/{n:02}.generation.json','sha256':h,'viewedNative':True,'viewedExportWithViewImage':True,'visualStatus':d['visualStatus']})
assert len(set(hashes))==16
edges=json.loads((rd/'edge-check.json').read_text(encoding='utf-8'))
assert all(max(e['nativeEdgeMaxAlpha_LRTB'])<64 for e in edges)
review={'group':'cast-W','checkedAt':datetime.now(timezone.utc).isoformat(),'frameCount':16,'durationMsEach':45,'totalMs':720,'technicalStatus':'passed: 16 distinct 1024 RGBA PNG, alpha0..255, SHA and references validated','visualStatus':'all 16 native results and exported frames actually viewed individually; initial 05/06 native right-ribbon clipping repaired through two additional builtin AI edits; true W back camera, same anatomical left support/right string-playing hand, 2 hands and 2 shoes retained','dynamicStatus':'pending: parent reported cua policy block for playback; no alternate route attempted, no playback pass claimed','clientIntegration':'not performed','modelEvidence':'configuration target gpt-image-2.5-sunburst/max; builtin submitted model/quality and actual returned model/quality null','sourceRetention':'native generated files still present outside project in tool-managed generated_images; source inventory provided for parent cleanup after final reference verification','frames':frames}
(rd/'REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
sources=[]
for p in list(rd.glob('*.generation.json'))+list((rd/'attempts').glob('*.generation.json')):
 d=json.loads(p.read_text(encoding='utf-8'))
 sources.append({'record':p.relative_to(root).as_posix(),'native':d['derivedFrom']['path'],'sha256':d['native']['sha256'],'status':'superseded' if 'attempts' in p.parts else 'accepted derived source'})
(rd/'native-source-inventory.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in review.items() if k!='frames'},ensure_ascii=False,indent=2))

