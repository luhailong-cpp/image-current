from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
batch=[]
for name in ['r14_c16','r15_c15','r15_c16','r16_c14','r16_c15','r16_c16']:
 T=Z/name;p=T/'progress.json';m=T/'active-native-map.json'
 if not p.exists():continue
 d=read(p);row={'tile':name,'progress':str(p),'progressSha256':sha(p),'status':d.get('status'),'activeNativeCount':len(read(m)) if m.exists() else 0,'formalAccepted':False,'internalArtQA':d.get('internalArtQA'),'externalNeighborSeamQA':d.get('externalNeighborSeamQA'),'candidate':d.get('candidate'),'context':d.get('context'),'assemblyManifest':d.get('assemblyManifest')}
 for key in ['candidate','context','assemblyManifest']:
  if row.get(key) and Path(row[key]).is_file():row[key+'Sha256']=sha(Path(row[key]))
 batch.append(row)
out={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'This production chat current near-complete batch only; no global map count and no historical re-audit','userRequest':'继续做完给我；优先补齐12–15/16及已有16/16少量必要返修','generationStopped':False,'inFlightRequestsAreNotCountedAsOutputs':True,'builtinOnly':True,'actualModel':None,'modelEvidence':'Builtin output returns no actual model selector/metadata','paidApiAllowed':False,'formalAccepted':False,'reservedExcluded':['r12_c13','r12_c14'],'items':batch,'knownPending':['r14c15 west W02 two unsuccessful native repair attempts retained; W01/W03 reviewed published','r15c16 internal short grout stub and west lower parapet shoulder under local repair; south3712..4096 protected','r16c16 N02 top-corner alignment needs external join QA; first west-column sources lack r16c15 neighbor and require final join'],'gitCommitOrPushClaimed':False}
folder=Z/'batch-checkpoints';folder.mkdir(exist_ok=True)
p=folder/(stamp+'.json')
with p.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
q=Z/'current-batch-checkpoint.json'
q.write_text(json.dumps({'path':str(p),'sha256':sha(p),'recordedAtUtc':out['recordedAtUtc'],'formalAccepted':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checkpoint':str(p),'sha256':sha(p),'items':[{'tile':x['tile'],'active':x['activeNativeCount'],'candidateSha256':x.get('candidateSha256'),'internalQA':x['internalArtQA']} for x in batch]},ensure_ascii=False))
