from pathlib import Path
import json, hashlib
from PIL import Image
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/10-xuanchaogui')
records=[]
for i in range(1,17):
 p=root/'runtime/cast/E'/f'{i:02d}.png'
 im=Image.open(p)
 sc=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 a=im.getchannel('A')
 records.append({'frame':i,'file':str(p.relative_to(root)),'sha256':digest,'size':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema(),'alphaBBox':a.getbbox(),'alphaBBox32':a.point(lambda v:255 if v>32 else 0).getbbox(),'shaMatchesSidecar':digest==sc['sha256'],'sidecar':str(Path(str(p)+'.generation.json').relative_to(root)),'promptExists':(root/sc['prompt']).exists(),'generationRecordExists':(root/sc['derivedFrom']['generationRecord']).exists(),'durationMs':sc['durationMs']})
report={'action':'cast','direction':'E','expectedFrames':16,'actualFrames':len(records),'duplicateSHA256':len(set(r['sha256'] for r in records))!=16,'checksPass':all(r['size']==[1024,1024] and r['mode']=='RGBA' and r['alphaExtrema']==(0,255) and r['shaMatchesSidecar'] and r['promptExists'] and r['generationRecordExists'] and r['durationMs']==45 for r in records),'individualVisualReview':'All 16 viewed individually; stable identity, E front three-quarter, crescent/branch/tassel side and one tail checked. 03 early-effect and 06 edge candidates replaced.','sequencePlayback':'pending root normal/0.25x/frame-step QA','clientIntegration':'not performed','frames':records}
(root/'provenance/cast/E/technical-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Preserve the rejected attempt exact prompt independently.
rp=root/'provenance/cast/E/06-edge-candidate.receipt.json'
candidate=json.loads(rp.read_text(encoding='utf-8'))
cp=root/'provenance/cast/E/06-edge-candidate.prompt.txt'
cp.write_text(candidate['prompt'],encoding='utf-8')
gp=root/'provenance/cast/E/06-edge-candidate.generation.json'
g=json.loads(gp.read_text(encoding='utf-8'))
g['prompt']=str(cp.relative_to(root));g['submittedParameters']['prompt']=g['prompt'];g['visualStatus']='rejected: right-edge claw margin'
gp.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False))

