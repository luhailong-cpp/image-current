import json,hashlib,sys
from pathlib import Path
Z=Path(__file__).resolve().parents[1]
stage=sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'path':p.as_posix(),'sha256':sha(p)}
qa=Z/'qa'
if stage=='upper':
 base=qa/'preflight-r10_c04-v1-assembly.json'
 tag='stair_upper'
 box=[1472,400,2726,1654]
else:
 oldtrace=qa/'repair-r10_c04-upper-v1-trace.json'
 tr=json.loads(oldtrace.read_text(encoding='utf8'))
 base=qa/'r10_c04-upper-v1-assembly-adapter.json'
 adapter={'schemaVersion':1,'context':tr['context'],'output':tr['candidate'],'derivedFromTrace':ref(oldtrace),'noResize':True,'noFeather':True}
 if not base.exists():base.write_text(json.dumps(adapter,indent=2)+'\n',encoding='utf8')
 tag='stair_lower'
 box=[1472,1424,2726,2678]
stem='r10_c04_'+tag+'_v1'
b=json.loads(base.read_text(encoding='utf8'))
m={'schemaVersion':1,'outputPrefix':'repair-r10_c04-'+stage+'-v1','baseAssembly':ref(base),'expectedBaseCandidateSha256':b['output']['sha256'],'notes':'Sequential native localized AI repair; four closed minimum-error hard boundaries, no resampling/feather/drawing. Candidate requires visual QA.','repairs':[{'id':tag,'source':ref(Z/'layout-only'/f'{stem}_native-target.png'),'repair':ref(Z/'native'/f'{stem}.png'),'generationRecord':ref(Z/'native'/f'{stem}.png.generation.json'),'tileContextBox':box,'repairBounds':[115,115,1139,1139],'margin':80}]}
path=qa/('repair-r10_c04-'+stage+'-v1.manifest.json')
path.write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
print(path.as_posix())

