import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((R/'candidate/manifest.json').read_text(encoding='utf-8'))
a=np.array(Image.open(m['candidate']))
coverage=np.zeros((4096,4096),dtype=np.uint8); checks=[]; errors=[]; refcount=0
for s in m['sources']:
 p=Path(s['path']); g=json.loads(Path(s['generationRecord']).read_text(encoding='utf-8'))
 for path,expected in [(p,s['sha256']),(g['prompt'],g['promptSha256']),(g['evidence']['request'],g['evidence']['requestSha256']),(g['evidence']['receipt'],g['evidence']['receiptSha256'])]:
  if sha(path)!=expected:errors.append({'path':str(path),'error':'sha mismatch'})
 for ref in g['references']:
  refcount+=1
  if sha(ref['path'])!=ref['sha256']:errors.append({'path':ref['path'],'error':'reference sha mismatch'})
 assert g['actualModel'] is None and g['actualQuality'] is None and g['submittedParameters']=={'model':None,'quality':None}
 assert g['configSnapshot']['model']=='gpt-image-2.5-sunburst' and g['configSnapshot']['quality']=='max'
 assert Image.open(p).size==(1254,1254) and g['nativeDimensions']==[1254,1254]
 x,y,x2,y2=s['destination']; coverage[y:y2,x:x2]+=1
 same=np.array_equal(a[y:y2,x:x2],np.array(Image.open(p))[115:1139,115:1139])
 assert same
 checks.append({'patch':s['patch'],'sha256':sha(p),'nativeSize':[1254,1254],'sourceCoreByteIdentical':same,'configTargetOnly':True,'actualAndSubmittedModelQualityNull':True,'sourceGenerationRecord':s['generationRecord']})
for axis in ('vertical','horizontal'):
 paths=[Path(i['qaNativeStrip']) for i in m['internalSeams'] if i['axis']==axis]
 for j in range(0,len(paths),4):
  batch=paths[j:j+4];out=Image.new('RGB',(1024,1088),'#333333');d=ImageDraw.Draw(out)
  for k,p in enumerate(batch):
   im=Image.open(p)
   if axis=='vertical':out.paste(im,(k*256,32));d.text((k*256+4,4),p.stem,fill='white')
   else:out.paste(im,(0,k*272+16));d.text((4,k*272),p.stem,fill='white')
  out.save(R/'qa'/f'contact-{axis}-{j//4+1}-native.png')
crosses=sorted((R/'qa').glob('cross-*-native.png'));out=Image.new('RGB',(1152,1200),'#333333');d=ImageDraw.Draw(out)
for i,p in enumerate(crosses):
 x=(i%3)*384;y=(i//3)*400;out.paste(Image.open(p),(x,y+16));d.text((x+3,y),p.stem,fill='white')
out.save(R/'qa/contact-crosses-native.png')
result={'tile':'r11_c09','status':'provenance_and_unscaled_coverage_verified' if not errors else 'errors','candidateSha256':sha(m['candidate']),'candidateSize':[4096,4096],'nativeSourceCount':len(checks),'referenceHashesVerified':refcount,'coverageMin':int(coverage.min()),'coverageMax':int(coverage.max()),'allCoresByteIdentical':True,'layoutPixelsDirectlyUsedInCandidate':False,'resizeApplied':False,'formalAccepted':False,'errors':errors,'sourceChecks':checks,'failedRequestRetained':{'stem':'p23-v1','receipt':str(R/'p23-v1.receipt.json'),'error':'network error, no image returned'},'modelQualityStatement':'Configuration target gpt-image-2.5-sunburst/max; builtin tool exposes no selectors or returned model/quality. Actual/submitted are null.'}
(R/'candidate/provenance-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='sourceChecks'},ensure_ascii=False))

