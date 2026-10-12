import json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/09-chishakui')
rows=[]
for direction,count in [('E',12),('W',8)]:
 for n in range(1,count+1):
  p=root/'runtime'/'attack'/direction/f'{n:02}.png'
  im=Image.open(p); a=im.getchannel('A'); sha=hashlib.sha256(p.read_bytes()).hexdigest()
  rp=p.with_suffix('.png.generation.json'); r=json.loads(rp.read_text(encoding='utf-8'))
  r['visualStatus']='single-frame-viewed; full-animation-playback-not-verified'
  r['visualReview']={'reviewer':'attack subagent','viewedAt':datetime.now(timezone.utc).isoformat(),'method':'actual generatedImage display at full frame; original E/W and style reference viewed','direction':direction,'rightHandHammer':True,'leftHandEmpty':True,'twoArmsTwoLegsTwoBoots':True,'noWingsNoTail':True,'camera':'three-quarter front lower-right' if direction=='E' else 'three-quarter back upper-left','animationReview':'not viewed in motion; no dynamic pass claimed'}
  rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
  rows.append({'file':str(p.relative_to(root)).replace('\\','/'),'sha256':sha,'dimensions':im.size,'mode':im.mode,'alphaExtrema':a.getextrema(),'subjectBBoxAlpha16':a.point(lambda x:255 if x>=16 else 0).getbbox(),'recordSHAEqualsFile':r['sha256']==sha,'promptExists':(root/r['prompt']).exists(),'receiptExists':(root/r['evidence']['receipt']).exists()})
report={'inspectedCount':len(rows),'allDimensions1024RGBA':all(x['dimensions']==(1024,1024) and x['mode']=='RGBA' for x in rows),'allGenuineAlpha':all(x['alphaExtrema']==(0,255) for x in rows),'uniqueSHA256':len(set(x['sha256'] for x in rows)),'allRecordedSHAAndTextReferencesValid':all(x['recordSHAEqualsFile'] and x['promptExists'] and x['receiptExists'] for x in rows),'scope':'E01..12 W01..08 only; root produces W09..12','rows':rows,'motionReview':'Not performed. Static per-frame review cannot establish no sliding/flicker or temporal pass.'}
(root/'records'/'attack-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))

