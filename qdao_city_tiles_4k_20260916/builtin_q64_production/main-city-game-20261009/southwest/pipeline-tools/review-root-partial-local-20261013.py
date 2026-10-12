from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=B/'r13_c06/pipeline/output/e7b5e8d88639ad53/assembly.json';a=read(ap)
assert not a['complete4kCandidate'] and a['verifiedNativeCount']==2
core=Image.open(a['output']['file']).convert('RGB');ctx=Image.open(a['contextOutput']['file']).convert('RGB')
assert sha(a['output']['file'])==a['output']['sha256'] and sha(a['contextOutput']['file'])==a['contextOutput']['sha256']
assert core.size==(2048,1024) and np.array_equal(np.array(core),np.array(ctx.crop((115,115,2163,1139))))
q=ap.parent/'root-local-qa-model-gate-20261013';q.mkdir(exist_ok=False)
records=[]
def save(im,name,derivation):
 p=q/name;im.save(p);records.append({'file':str(p),'sha256':sha(p),'pixels':list(im.size),'derivation':derivation,'sourceResampling':False,'QAOnly':True})
save(core.crop((896,0,1152,1024)),'internal-V1.native.png',{'source':a['output'],'coreBox':[896,0,1152,1024]})
cat=read(B/'current-candidates.json')['tiles']
top=cat['r12_c06']['candidate'];left=cat['r13_c05']['candidate']
for e in [top,left]:assert sha(e['file'])==e['sha256']
ti=Image.open(top['file']).convert('RGB');li=Image.open(left['file']).convert('RGB')
for c in range(2):
 x=c*1024;pan=Image.new('RGB',(1024,256));pan.paste(ti.crop((x,3968,x+1024,4096)),(0,0));pan.paste(core.crop((x,0,x+1024,128)),(0,128))
 save(pan,f'external-top-{c+1}.native.png',{'top':top,'bottom':a['output'],'topBox':[x,3968,x+1024,4096],'bottomBox':[x,0,x+1024,128],'joinY':128})
pan=Image.new('RGB',(256,1024));pan.paste(li.crop((3968,0,4096,1024)),(0,0));pan.paste(core.crop((0,0,128,1024)),(128,0))
save(pan,'external-left-1.native.png',{'left':left,'right':a['output'],'joinX':128,'leftBox':[3968,0,4096,1024],'rightBox':[0,0,128,1024]})
core.resize((1024,512),Image.Resampling.LANCZOS).save(q/'overview-QA-only.png')
atomic_json(q/'manifest.json',{'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'assembly':str(ap),'assemblySha256':sha(ap),'output':a['output'],'nativeQA':records,'availableCoverage':[2048,1024],'missingSlots':a['missingPatchIds'],'modelGateSource':'D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md','newGenerationCalls':0,'internalPassed':False,'formalAccepted':False,'visualReviewStatus':'pending_actual_view'})
print(q)
