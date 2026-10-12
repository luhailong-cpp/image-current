"""Read-only production inputs; write tile-local preparation evidence only."""
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;TILE=HERE.parent;ZONE=TILE.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=read(TILE/'coordinates.json');assert plan['coreWorldBox']==[49152,24576,53248,28672]
assert len(plan['patches'])==16
guides=[]
for v in plan['patches']:
    r,c=int(v['id'][1]),int(v['id'][2]);x,y=49152+(c-1)*1024,24576+(r-1)*1024
    assert v['coreWorldBox']==[x,y,x+1024,y+1024]
    assert v['contextWorldBox']==[x-115,y-115,x+1139,y+1139] and v['coreCrop']==[115,115,1139,1139]
    p=Path(v['guide']);assert sha(p)==v['guideSha256'];im=Image.open(p);assert im.size==(1254,1254)
    meta=read(str(p)+'.generation.json');assert meta['assetRole']=='layout-only; never game art'
    guides.append({'id':v['id'],'sha256':sha(p),'dimensions':[1254,1254],'role':'layout-only geometry guide, not native art'})
checks=read(HERE/'north-context-check.json')['checks'];assert len(checks)==4
for check in checks:
    assert 'north' in check['availableDirections']
    for s in check['sources']:assert sha(s['file'])==s['sha256']
north=ZONE/'r06_c13/candidates/r06_c13.candidate.png';before=sha(north);im=Image.open(north).convert('RGB');assert im.size==(4096,4096)
strips=[]
for c in range(4):
    box=[1024*c,3636,1024*(c+1),4096];p=HERE/f'north-candidate-boundary-c{c+1}-1to1.png';im.crop(box).save(p)
    strips.append({'file':str(p),'sha256':sha(p),'sourceBox':box,'worldBox':[49152+box[0],20480+box[1],49152+box[2],24576],'pixelsPerSourcePixel':1})
assert sha(north)==before
assert not list((TILE/'native').glob('*.png')) and not list((TILE/'prompts').glob('*.request.json'))
record={'tile':TILE.name,'createdAt':datetime.now(timezone.utc).isoformat(),'coordinates':str(TILE/'coordinates.json'),'coordinatesSha256':sha(TILE/'coordinates.json'),'coreWorldBox':plan['coreWorldBox'],'preparedGuideCount':16,'guides':guides,'northCandidate':str(north),'northCandidateSha256':before,'northCandidateBoundaryCrops':strips,'northContextReadyPatchIds':['p11','p12','p13','p14'],'candidateCoreAuthoritativeTopRows':115,'nativeContextRows':230,'generatedNativeCount':0,'imageGenerationCalls':0,'formalAcceptedCount':0,'oldCandidatesWritten':False,'sharedProgressWritten':False,'visualStatus':'boundary crops pending review','nextAction':'Wait for parent release after current 2x2 closure; before drawing refresh north candidate SHA and context, then attach all approved references.'}
save(HERE/'preparation-audit.json',record)
save(TILE/'tile-progress.json',{'tile':TILE.name,'status':'prepared-waiting-for-parent-drawing-release','preparedGuideCount':16,'nativeCount':0,'selectedCoreCount':0,'remainingCoreCount':16,'completeCandidateCount':0,'internalPassed4kCount':0,'formalAcceptedCount':0,'nextPatch':'p11','inflightGeneration':None,'actualModel':None,'actualQuality':None,'northCandidateSha256':before,'preparationAudit':str(HERE/'preparation-audit.json'),'generationHold':'Parent will release drawing after current 2x2 beam finish. No image generation authorized yet for this tile.'})
print(json.dumps({'tile':TILE.name,'coreWorldBox':plan['coreWorldBox'],'preparedGuideCount':16,'northCandidateSha256':before,'generatedNativeCount':0,'imageGenerationCalls':0}))
