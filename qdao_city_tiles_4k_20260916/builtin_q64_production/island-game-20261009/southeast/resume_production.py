from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now
base=ROOT.parent.parent
control=base/'resume-production-20261010/production-resume.json'
contract=ROOT.parent/'production-contract.json';gate=base/'capacity-layout-gate-20261010.json'
resume=read(control);ct=read(contract);g=read(gate)
assert resume['newArtworkGenerationAllowed'] and not g['holdGenerationAtNewCoordinates']
refs=read(ROOT/'references.json')
history=ROOT/'references-before-resume-20261010.json'
if not history.exists():write(history,refs)
p=Path(ct['primaryStyleReference']);assert sha(p)==ct['primaryStyleSha256']
refs[-1]={'file':p.as_posix(),'role':'primary approved user-provided mail Daoist Q painting style; no UI, text, characters or night lighting','sha256':sha(p),'nativePixels':list(Image.open(p).size),'effectiveFrom':now(),'authority':str(control)}
for r in refs:assert Path(r['file']).exists() and sha(Path(r['file']))==r['sha256']
write(ROOT/'references.json',refs)
config=read(Path('D:/work/image/config/image-generation.json'))
for f in ROOT.glob('progress*.json'):
 d=read(f);d.update(configSnapshot=config,status='resumed_existing_coordinate_production',lastError=None,updatedAt=now())
 d['nextStep']='Use current approved references; complete existing missing cores and2x2 shared-edge QA, then remainder of assigned zone.'
 write(f,d)
d=read(ROOT/'production-state.json');d.update(actualProgress='resumed',updatedAt=now(),resumeAuthority=str(control),inFlight=False)
d['rootActiveTile'].update(hold=None,nextStep='r11c12 remaining6 cores, retain10 current cores')
write(ROOT/'production-state.json',d)
ack={'schemaVersion':1,'zone':'southeast','resumedAtUtc':now(),'status':'actual_production_resumed','authority':{'control':str(control),'sha256':sha(control),'contract':str(contract),'contractSha256':sha(contract),'gate':str(gate),'gateSha256':sha(gate)},'currentCoordinates':{'root':'r11_c12,10of16 existingcores','tile_left':'r10_c11,p14 existing','tile_right':'r09_c13,two post/beam seams unresolved','coordinate_audit':'r08_c12,candidate-v3 roof and sharpness seams unresolved'},'nextMilestone':['Complete r10_c11 and close r09c11/r09c12/r10c11/r10c12 neighborhood','Keep current r11c12 working art and finish remaining6cores','Fix existing r09c13/r08c12 geometry before extending their edges','Continue remaining49-tile zone after2x2 seam QA'],'fullyCovered4kCount':5,'internalPassed4kCount':3,'externalPassed4kCount':0,'formalAcceptedCount':0,'newPrimaryStyle':refs[-1],'historyUntouched':True,'builtinOnly':True,'paidApiAllowed':False,'worldSize':None,'capacity5000Validated':False,'layoutAndArtGridUnchanged':True,'localEntranceReview':resume['localEntranceReview']['island-game-20261009']}
write(ROOT/'resume-ack-20261010.json',ack)
print({'resumed':True,'primaryStyle':refs[-1],'modelTarget':config['model'],'qualityTarget':config['quality'],'actualModel':None,'actualQuality':None})
