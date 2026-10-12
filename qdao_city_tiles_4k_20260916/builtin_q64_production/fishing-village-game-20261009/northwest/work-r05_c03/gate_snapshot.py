from pathlib import Path
import json,hashlib,sys,importlib.util
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;R=W.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=[read(p) for p in sorted((W/'selections').glob('*.json'))]
assert len(sources)==4 and all(e['row']==1 for e in sources)
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=np.asarray(Image.open(sources[0]['file']).convert('RGB'));ids=np.ones((1254,1254),dtype=np.uint8);seams=[]
for i,e in enumerate(sources[1:],2):
 assert sha(e['file'])==e['sha256']
 a,ids,s=m.append_hard(a,ids,np.asarray(Image.open(e['file']).convert('RGB')),np.ones((1254,1254),dtype=np.uint8)*i,f'first-row-col{i-1}-to-{i}');seams.append(s)
row=Image.fromarray(a[115:1139,115:4211]);p=W/'output/r05_c03.first-row.partial.png';row.save(p)
old=R/'work-r04_c03/output/r04_c03.candidate.png'
qa=Image.new('RGB',(4096,400));qa.paste(Image.open(old).crop((0,3896,4096,4096)),(0,0));qa.paste(row.crop((0,0,4096,200)),(0,200))
q=W/'qa/gate-north-actual-boundary-100pct.png';qa.save(q)
contact=Image.new('RGB',(1024,1600))
for c in range(4):
 seg=qa.crop((c*1024,0,(c+1)*1024,400));sp=W/f'qa/gate-north-actual-segment-{c+1}.png';seg.save(sp);contact.paste(seg,(0,c*400))
cp=W/'qa/gate-north-contact-100pct.png';contact.save(cp)
missing=[]
for e in sources:
 g=read(e['file']+'.generation.json')
 for ref in g['references']:
  if not Path(ref['file']).is_file() and ref['file'] not in missing:missing.append(ref['file'])
ack={'createdAt':datetime.now(timezone.utc).isoformat(),'gate':str(R.parent.parent/'capacity-layout-gate-20261010.json'),'status':'generation-held-capacity-layout-gate','inFlight':False,'newImageRequestsAllowed':False,'generatedCoordinates':[[1,c] for c in range(1,5)],'generatedNativeOutputs':len(list((R/'native').glob('r05_c03_*.png'))),'selectedSources':sources,'remainingCoordinates':[[r,c] for r in range(2,5) for c in range(1,5)],'lastAttempt':{'coordinate':[2,1],'version':1,'result':'failed-before-output-missing-required-reference','errorFile':str(W/'receipts/r05_c03_s02_s01_v01.error.json')},'missingReferencesForReplay':missing,'artworkDeleted':False,'formalAccepted':False,'partialAssembly':{'file':str(p),'sha256':sha(p),'size':list(row.size),'operation':'unscaled native min-error hard-cut row then integer core crop; NOT full tile','sources':sources,'paths':seams},'northBoundaryEvidence':{'file':str(q),'sha256':sha(q),'previousCandidate':str(old),'previousSha256':sha(old),'operation':'previous actual tile bottom200 above current assembled first-row top200, no resizing','contactSheet':str(cp),'contactSha256':sha(cp)},'capacityRisks':['No capacity-5000 validation; shared-world scale still unconfirmed.','r04_c03 wall/paving and r05_c03 tall fishing-net/post silhouettes cross cell boundaries; collision/occlusion masks must distinguish hanging net from ground-level walkability.','r05_c03 current art covers only north1024 pixels; do not infer completed southern lanes/buildings from this partial image.','Large post near local x3000 is a likely ground-level blocker; exact footprint is not established by artwork alone.'],'visualLimitation':'North s01_s04 wood retains tonal mismatch; no geometry offset observed; formal external acceptance pending.'}
write(W/'qa/capacity-gate-ack.json',ack)
write(W/'progress.json',{'tile':'r05_c03','requiredFragments':16,'generationOutputs':ack['generatedNativeOutputs'],'selectedCandidateFragments':4,'formalAccepted':False,'inFlight':False,'status':ack['status'],'lastAttemptError':ack['lastAttempt'],'next':'Await root capacity gate release and restoration of required mail reference; no new requests'})
print(json.dumps({'ack':str(W/'qa/capacity-gate-ack.json'),'ackSha256':sha(W/'qa/capacity-gate-ack.json'),'partialSha256':sha(p),'northQaSha256':sha(q),'missingReferences':missing}))
