from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil
Z=Path(__file__).resolve().parent
T=Z/'r07_c13'
A=T/'qa/core-baseline/f30ef04cf1155a6e57a2/assembly.json'
B=A.parent/'r07_c13-core-baseline.candidate.png'
D=T/'qa/finish-20261011'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=json.loads(A.read_text(encoding='utf-8'))
assert a['validSelectedNativeCount']==16 and not a['invalidSelectedSources']
assert sha(B)==next(v['sha256'] for v in a['artifacts'] if v['kind']=='complete-4k-candidate-unreviewed')
C=T/'candidates/r07_c13.candidate.png'
if not C.exists():shutil.copy2(B,C)
assert sha(C)==sha(B),'Do not overwrite repaired candidate'
save(Path(str(C)+'.generation.json'),{'file':str(C),'sha256':sha(C),'width':4096,'height':4096,'format':'PNG','assetRole':'complete4kCandidate; internal review pending; not formal accepted','derivedFrom':[{'file':str(B),'sha256':sha(B),'assembly':str(A),'assemblySha256':sha(A)}],'operation':{'method':'exact baseline PNG copy; sixteen native1024 cores','resized':False,'feathered':False},'actualModel':None,'actualQuality':None,'formalAcceptedCount':0})
save(T/'tile-progress.json',{'tile':T.name,'updatedAt':datetime.now(timezone.utc).isoformat(),'status':'complete_4k_candidate_internal_repairs_pending','nativeCount':len(list((T/'native').glob('*.png'))),'selectedCoreCount':16,'remainingCoreCount':0,'fullyCovered4kCount':1,'completeCandidateCount':1,'internalPassed4kCount':0,'formalAcceptedCount':0,'candidate':str(C),'candidateSha256':sha(C),'assembly':str(A),'pendingReview':'24 internal pairs and9 junctions; two structural repairs identified','nextPatch':None,'inflightGeneration':None,'actualModel':None,'actualQuality':None,'nextStep':'Apply bounded native repairs to plaque frame and right roof eave, inspect remaining seams.'})
im=Image.open(B).convert('RGB')
for name,box in [('m01-plaque',[397,1720,1651,2974]),('m02-eave',[2445,1550,3699,2804]),('m03-ridge',[1550,1500,2804,2754])]:
    f=D/'contexts'/(name+'.png')
    if f.exists():continue
    f.parent.mkdir(parents=True,exist_ok=True);im.crop(box).save(f)
    save(Path(str(f)+'.generation.json'),{'file':str(f),'sha256':sha(f),'derivedFrom':[{'file':str(B),'sha256':sha(B)}],'operation':{'type':'integer native pixel crop','box':box,'resized':False},'assetRole':'native art edit target'})
q=json.loads((Z/'work-queue-20261010.json').read_text(encoding='utf-8'))
q['owners']=[{'agent':'root','scope':'r07_c13 full candidate QA and bounded repairs; zone records'},{'agent':'native_quality','scope':'r08_c13 all16 cores, internal/north checks'},{'agent':'east_tile_resume','scope':'r07_c14 all16 cores, internal/north/west checks; r07_c13 p24 complete'},{'agent':'coordinate_audit','scope':'r07_c13 read-only independent seam review'}]
q['notes']=[v for v in q['notes'] if not v.startswith('r08_c13/r08_c14')]
q['notes'].append('r08_c13 actively drawing; r08_c14 remains in fixed group, not yet started. Existing acceleration assignment exclusions were checked and do not intersect this northeast group.')
q['updatedAt']=datetime.now(timezone.utc).isoformat();save(Z/'work-queue-20261010.json',q)
print(json.dumps({'candidate':str(C),'sha256':sha(C),'repairDirectory':str(D),'selected':16,'internalPass':0}))

