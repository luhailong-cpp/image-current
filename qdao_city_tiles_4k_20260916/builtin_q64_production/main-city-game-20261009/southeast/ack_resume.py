from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
control=B.parent.parent/'resume-production-20261010'/'production-resume.json';gate=B.parent.parent/'capacity-layout-gate-20261010.json';contract=read(B.parent/'production-contract.json')
assert read(control)['newArtworkGenerationAllowed'] and not read(gate)['holdGenerationAtNewCoordinates']
p=read(B/'progress.json');assert sha(p['candidateFile'])==p['candidateSha256']
refs=[]
for key in ['layoutReference','detailStyleReference','primaryStyleReference']:
    path=contract[key];refs.append({'role':key,'path':path,'sha256':sha(path),'size':list(Image.open(path).size)})
assert refs[2]['sha256']==contract['primaryStyleSha256']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ack={'schemaVersion':1,'resumedAtUtc':now,'resumeControl':str(control),'resumeControlSha256':sha(control),'contractSha256':sha(B.parent/'production-contract.json'),'gateHoldReleased':True,'zone':'southeast','sourceCandidate':{'tile':'r13_c13','file':p['candidateFile'],'sha256':p['candidateSha256'],'internalPassed':True,'externalPassed':False},'next2x2':['r13_c13','r13_c14','r14_c13','r14_c14'],'nextStep':'Extend east r13_c14 and south r14_c13 from approved current native boundaries, then southeast r14_c14; inspect entire shared seams and 4tile intersection before further expansion.','referencesActuallyInspected':refs,'modelConfigSnapshot':read(Path('D:/work/image/config/image-generation.json')),'actualModel':None,'actualQuality':None,'builtinOnly':True,'paidApiAllowed':False,'newImageCallsAtAck':0,'inFlightAtAck':0,'worldSize':None,'capacity5000Validated':False,'historicalRecordsModified':False,'newReferenceResolution':'Use newly authorized user JPG on FUTURE requests only; original missing PNG records remain unchanged.','entireZoneTaskComplete':False}
write(B/'resume-ack-20261010.json',ack)
p.update(updatedAt=now,status='resumed_native_2x2_expansion',capacityGateActive=False,productionResumeAck=str(B/'resume-ack-20261010.json'),newPrimaryReferenceResolved=True,newPrimaryStyleReference=refs[2],currentTile='r13_c14',currentPatch='p01_01',nextStep=ack['nextStep'])
write(B/'progress.json',p)
Q=B/'resume-review';Q.mkdir(exist_ok=True)
im=Image.open(contract['layoutReference'])
for name,r,c in [('r13_c14',13,14),('r14_c13',14,13),('r14_c14',14,14)]:
    box=[(c-1)*4096,(r-1)*4096,c*4096,r*4096];f=Q/f'{name}-layout-preview-only.png'
    im.transform((1254,1254),Image.Transform.EXTENT,[v*1254/65536 for v in box],Image.Resampling.NEAREST).save(f)
    write(str(f)+'.derived.json',{'role':'layout preview only,notart','box':box,'source':contract['layoutReference'],'sourceSha256':sha(contract['layoutReference']),'resampled':True})
print(json.dumps({'resumed':True,'next2x2':ack['next2x2'],'currentCandidates':1,'formalAccepted':0,'refs':refs}))

