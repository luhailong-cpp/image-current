"""Record the independent review already performed on seven native QA crops."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,uuid
Z=Path(__file__).resolve().parent
T=Z/'r15_c13';Q=T/'repairs-resume-20261012'/'local-qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,d):
    temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,p)
latest=read(T/'candidate'/'latest-assembly.json')
assert latest['candidate']['sha256']=='c7d01db8f1c02de10c81f230c68331021b5dc6e676190802ae2b9bdcf7e4e51f'
for key in ('candidate','context','manifest'):assert sha(latest[key]['path'])==latest[key]['sha256']
paths=[Q/f'native-halo-narrow24-north-quarter-{n}.png' for n in range(1,5)]+[Q/f'native-halo-narrow24-junction-{n}.png' for n in (1024,2048,3072)]
evidence=[{'path':str(p),'sha256':sha(p),'resized':False,'reviewedAtNativePixels':True} for p in paths]
record=Q/'root-independent-north-review-20261012.json'
report={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','reviewMethod':'All seven evidence images viewed using view_image detail original during the current resumed production run. Record persisted after continuation compaction.','candidate':latest['candidate'],'context':latest['context'],'composition':latest['manifest'],'evidence':evidence,'result':'north_local_pass_with_texture_watch','findings':['No visible geometry step, doubled outline or strong straight material band across the inspected north join.','Minor local texture variation remains a cosmetic watch item.'],'scope':'Exact selected halo24 candidate, full north join quarters and three internal junctions; does not authorize other halo pixels or other neighbor edges.','remainingNeighborQA':['east','south','west'],'formalAccepted':False}
if record.exists():
    old=read(record);assert old['candidate']==report['candidate'] and old['evidence']==report['evidence']
else:
    with record.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
pointer={'path':str(record),'sha256':sha(record)}
for p in [T/'progress.json',T/'candidate'/'latest-assembly.json']:
    d=read(p);d['independentNorthQA']=pointer;d['externalNeighborSeamQA']='north_local_pass_with_texture_watch; east_south_west_joint_pending';d['nextStep']='Continue east/south/west neighboring current-core joint review; north local review recorded.'
    if 'remainingQA' in d:
        for item in d['remainingQA']:
            if item.get('id')=='north-independent-joint-review':item['status']='north_local_pass_with_texture_watch';item['independentReview']=pointer
    atomic(p,d)
print(json.dumps(pointer))
