from pathlib import Path
from PIL import Image
import json,hashlib,datetime,re
z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):
 p=Path(p)
 return {'path':str(p),'sha256':sha(p),'role':role}
names=['r06_c12_p22-v1','r06_c12_p22-v2','r06_c12_p32-v1','r06_c12_p42-v1','r06_c12_p42-v2']
records=[]
for n in names:
 p=z/'native'/f'{n}.png'
 r=read(str(p)+'.generation.json')
 assert r['sha256']==sha(p)
 assert [r['width'],r['height']]==[1254,1254]
 assert r['submittedParameters']=={'model':None,'quality':None}
 assert r['actualModel'] is None and r['actualQuality'] is None
 for role in ('prompt','receipt'):
  assert r[role]['sha256']==sha(r[role]['path'])
 receipt=read(r['receipt']['path'])
 assert len(receipt['request']['referenced_image_paths']) in (4,5)
 for item in r['references']:assert item['sha256']==sha(item['path'])
 records.append(ref(str(p)+'.generation.json','independent builtin image_gen output'))
for n in ['r06_c12_p22-v1','r06_c12_p22-v2']:
 for side in ['left-right-seams','top-seam']:
  p=z/'qa'/f'{n}-{side}.png'
  inputs=[n]+(['r06_c12_p21-v2','r06_c12_p23-v1'] if side=='left-right-seams' else ['r06_c12_p12-bridge-candidate'])
  sources=[]
  for s in inputs:
   sp=z/'native'/f'{s}.png'
   suffix='.derived.json' if 'bridge-candidate' in s else '.generation.json'
   sources.append({**ref(sp,'native source used at 1:1'), 'provenanceRecord':str(sp)+suffix})
  save(str(p)+'.derived.json',{'file':str(p),'sha256':sha(p),'derivedFrom':sources,
   'operation':'1:1 crop and opaque paste along 1024-core boundaries; no resize, blend, feather or painting',
   'reproductionScript':str(z/'qa/r06_c12_p22-seams.py'),'purpose':'native-resolution QA only'})
handoff={'schemaVersion':1,'updatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'owner':'middle_column','assignedPatches':['r06_c12_p22','r06_c12_p32','r06_c12_p42'],
 'scope':'Only assigned native/records/guides/qa prefixes written. Shared progress and contract not modified.',
 'generatedNativeCountAdded':5,'candidateNativeCount':3,'usableNativeCountAdded':0,
 'countMeaning':'3 candidate identities chosen for continuing coverage, not seamless accepted natives; generated count includes two repair calls',
 'complete4kCountAdded':0,'formalAcceptedCountAdded':0,
 'generationRecords':records,
 'candidateFiles':[
  {'file':str(z/'native/r06_c12_p22-v2.png'),'sha256':sha(z/'native/r06_c12_p22-v2.png'),
   'status':'candidate_known_right_seam_geometry_failure','coreBox':[115,115,1139,1139],
   'reviews':{'top':'100% strip reviewed; fish/divider silhouettes substantially continuous, small texture changes','left':'100% strip reviewed; post/rim/paving substantially continuous','right':'FAIL: front gold rim drops too low relative to p23-v1, with step and fish interruption; targeted v2 repair did not resolve geometry'},
   'qa':[str(z/'qa/r06_c12_p22-v2-left-right-seams.png'),str(z/'qa/r06_c12_p22-v2-top-seam.png')]},
  {'file':str(z/'native/r06_c12_p32-v1.png'),'sha256':sha(z/'native/r06_c12_p32-v1.png'),
   'status':'candidate_top_left_reviewed_right_pending','coreBox':[115,115,1139,1139],
   'reviews':{'top':'100% strip reviewed; leg, lower timber and floor joints substantially continuous with slight microtexture/color changes','left':'100% strip reviewed; paving and rope post substantially continuous','right':'No right neighbor existed at generation; unverified'},
   'qa':[str(z/'qa/r06_c12_p32-v1-top-seam.png'),str(z/'qa/r06_c12_p32-v1-left-seam.png')]},
  {'file':str(z/'native/r06_c12_p42-v2.png'),'sha256':sha(z/'native/r06_c12_p42-v2.png'),
   'status':'candidate_top_left_reviewed_right_and_bottom_pending','coreBox':[115,115,1139,1139],
   'reviews':{'internal':'v2 removed redundant forked timber next to left post; counter front now single continuous beam','top':'100% strip reviewed; back rim, blue fish and floor substantially continuous with minor detail/color changes','left':'100% strip reviewed; rope post and fish silhouettes substantially continuous','right':'No right neighbor existed at generation; unverified','bottom':'External tile boundary unverified'},
   'qa':[str(z/'qa/r06_c12_p42-v2-top-seam.png'),str(z/'qa/r06_c12_p42-v2-left-seam.png')]}
 ],
 'notChosen':{'r06_c12_p22-v1':'v2 continuing candidate; neither solves right seam','r06_c12_p42-v1':'v2 repairs redundant forked timber'},
 'nextStep':'Use selected p32-v1 and p42-v2 as left constraints for p33/p43. Repair p22/p23 cross-column seam with native bridge via image_gen, then inspect every internal/external seam at 100%. Do not feather geometry misalignment.',
 'actualModel':None,'actualQuality':None,'paidApiUsed':False,'nativeUpscalingPerformed':False,
 'navigationValidated':False,'clientValidated':False,'capacity5000Validated':False}
save(z/'records/r06_c12_p22-middle-column-handoff.json',handoff)
print(json.dumps({'generatedNativeCountAdded':5,'candidateNativeCount':3,'complete4kCountAdded':0,'formalAcceptedCountAdded':0,'integrity':'5 output files, prompts, receipts and direct reference hashes verified','handoff':str(z/'records/r06_c12_p22-middle-column-handoff.json')},ensure_ascii=False))

