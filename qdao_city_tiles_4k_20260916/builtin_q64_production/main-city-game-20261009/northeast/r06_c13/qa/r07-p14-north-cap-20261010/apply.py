"""Replay original 16 cores + six repairs, then one binary north-cap addition."""
from pathlib import Path
from PIL import Image,ImageChops
import argparse,json,hashlib,importlib.util,shutil
from datetime import datetime,timezone
import numpy as np
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1];ZONE=TILE.parent
FINISH=TILE/'qa/finish-20261010';PREFIX=FINISH/'records/candidate-replay.json'
OLD='2920e92f3c34f6ae2e73a5a9e52fe862adef3230487c2df2f98f48a7de5b0b2e'
PREFIX_SHA='3825c26a41a14870c48c2d2e85bebe8459889f30b298c8e4e20b4d61117b3cbd'
PROPOSAL=ZONE/'r07_c13/qa/p14-north-cap/integration-proposal.json'
CANDIDATE=TILE/'candidates/r06_c13.candidate.png';BACKUP=HERE/'before-2920e92f.png'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def replay():
    assert sha(PREFIX)==PREFIX_SHA and sha(BACKUP)==OLD
    spec=importlib.util.spec_from_file_location('original_r06_replay',FINISH/'apply.py');previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
    t,plan=previous.assemble.load_plan('r06_c13');native,evidence,missing,invalid=previous.assemble.inspect_sources(t,plan);assert not missing and not invalid and len(native)==16
    canvas=previous.assemble.compose(plan,native).convert('RGB');prefix=read(PREFIX);assert len(prefix['operations'])==6
    for op in prefix['operations']:previous.operation(canvas,op)
    before=Image.open(BACKUP).convert('RGB');assert ImageChops.difference(canvas,before).getbbox() is None,'Prior full source chain differs from frozen 2920 image'
    p=read(PROPOSAL);source=Path(p['source']);maskpath=Path(p['mask']);assert sha(source)==p['sourceSha256'];assert sha(maskpath)==p['maskSha256']
    st,sp=previous.assemble.load_plan('r07_c13');item=next(v for v in sp['patches'] if v['id']=='p14');src,source_evidence=previous.assemble.inspect_source(st,item);assert source_evidence['sha256']==p['sourceSha256']
    mask=Image.open(maskpath);assert mask.mode=='L' and mask.size==(1254,1254) and {i for i,v in enumerate(mask.histogram()) if v}<={0,255}
    op=p['integerTileOperations'][0];assert op['tile']=='r06_c13' and op['sourceCrop']==[280,88,450,115] and op['maskCrop']==op['sourceCrop'] and op['destinationTileXY']==[3237,4069]
    crop=op['sourceCrop'];dest=tuple(op['destinationTileXY']);localmask=mask.crop(crop);canvas.paste(src.crop(crop),dest,localmask)
    fullmask=Image.new('L',(4096,4096));fullmask.paste(localmask,dest)
    diff=ImageChops.difference(before,canvas);outside=diff.copy();outside.paste((0,0,0),(0,0),fullmask);assert outside.getbbox() is None
    diffbox=diff.getbbox();assert diffbox and diffbox[0]>=3265 and diffbox[1]>=4077 and diffbox[2]<=3356 and diffbox[3]<=4096
    pixels=int(np.count_nonzero(np.any(np.asarray(before)!=np.asarray(canvas),axis=2)))
    return canvas,{'prefixRecipe':str(PREFIX),'prefixRecipeSha256':PREFIX_SHA,'prefixImage':str(BACKUP),'prefixImageSha256':OLD,'source':str(source),'sourceSha256':p['sourceSha256'],'sourceGenerationRecord':source_evidence['generationRecord'],'sourceAudit':source_evidence,'mask':str(maskpath),'maskSha256':p['maskSha256'],'proposal':str(PROPOSAL),'proposalSha256':sha(PROPOSAL),'operation':op,'fullMaskBox':fullmask.getbbox(),'changedPixelBox':diffbox,'changedPixelCount':pixels,'outsideMaskPixelIdentical':True,'binaryMask':True,'sourceResized':False,'imageBlur':False,'geometricWarp':False,'feathering':False,'original16NativeCoreCount':16,'originalRepairLayerCount':6,'appendedLayerCount':1,'formalAcceptedCount':0,'actualModel':None,'actualQuality':None}
def render_shared(canvas):
    p14=Image.open(ZONE/'r07_c13/native/p14.png').convert('RGB');x0,y0=52109,24461
    # Exact context around the cap, includes current north candidate and p14 core.
    image=p14.copy();image.paste(canvas.crop([2957,3981,4096,4096]),(0,0));image.crop([230,50,500,250]).save(HERE/'after-shared-cap-1to1.png')
    return str(HERE/'after-shared-cap-1to1.png')
def main(check):
    if check:
        recipe=read(HERE/'replay.json');assert sha(CANDIDATE)==recipe['outputSha256'];canvas,record=replay();assert ImageChops.difference(canvas,Image.open(CANDIDATE).convert('RGB')).getbbox() is None
        result={'pixelReplayIdentical':True,'outputSha256':sha(CANDIDATE),'prefixImageSha256':OLD,'outsideMaskPixelIdentical':True,'changedPixelBox':record['changedPixelBox'],'changedPixelCount':record['changedPixelCount'],'nativeSourcesVerified':16,'repairLayerCount':7,'capNativeSourceVerified':True,'formalAcceptedCount':0};save(HERE/'verification.json',result);print(json.dumps(result));return
    assert sha(CANDIDATE)==OLD and not BACKUP.exists() and not (HERE/'replay.json').exists()
    shutil.copy2(CANDIDATE,BACKUP);shutil.copy2(str(CANDIDATE)+'.generation.json',HERE/'before-generation.json');shutil.copy2(TILE/'tile-progress.json',HERE/'before-tile-progress.json')
    canvas,record=replay();tmp=HERE/'candidate-new.png';canvas.save(tmp);newsha=sha(tmp);assert sha(CANDIDATE)==OLD
    tmp.replace(CANDIDATE)
    record.update({'output':str(CANDIDATE),'outputSha256':newsha,'createdAt':datetime.now(timezone.utc).isoformat(),'status':'one binary cap appended; pixel verification passed, final visual review pending'});save(HERE/'replay.json',record)
    evidence=render_shared(canvas);side=read(HERE/'before-generation.json');side.update({'sha256':newsha,'recipe':str(HERE/'replay.json'),'recipeSha256':sha(HERE/'replay.json'),'previousGenerationRecord':{'file':str(HERE/'before-generation.json'),'sha256':sha(HERE/'before-generation.json')},'sourceReplay':str(HERE/'apply.py'),'repairLayerCount':7,'appendedRepairLayer':{k:record[k] for k in ['source','sourceSha256','mask','maskSha256','operation','sourceGenerationRecord']},'appendedRepairReview':str(HERE/'visual-review.json'),'pixelReplayVerified':False});save(str(CANDIDATE)+'.generation.json',side)
    progress=read(TILE/'tile-progress.json');progress.update({'updatedAt':datetime.now(timezone.utc).isoformat(),'candidateSha256':newsha,'sourceReplay':str(HERE/'apply.py'),'additionalBoundaryReview':str(HERE/'visual-review.json'),'nextStep':'Root re-export prior 2x2 shared windows and refresh group source snapshot after tiny south-edge cap addition.'});save(TILE/'tile-progress.json',progress)
    print(json.dumps({'newCandidateSha256':newsha,'oldCandidateSha256':OLD,'changedPixelBox':record['changedPixelBox'],'changedPixelCount':record['changedPixelCount'],'outsideMaskPixelIdentical':True,'sharedEvidence':evidence},ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();main(a.check)
