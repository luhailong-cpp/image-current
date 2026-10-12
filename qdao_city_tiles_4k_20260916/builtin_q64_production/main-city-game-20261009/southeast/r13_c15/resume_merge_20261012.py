"""Offline replay of three retained native repairs onto the selected ornaments base.

Build is versioned and non-publishing; publish requires a visual QA record.
No image generation, resampling, historical-record edits, or zone writes.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, uuid
import numpy as np
from PIL import Image

T=Path(__file__).resolve().parent
Z=T.parent
AUTH=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
FREEZE=Z/'migration-freeze-20261011.json'
CHECKPOINT=T/'repairs/structure-checkpoint-20261011.json'
BASE_SHA='f8e09b2334b83e447e93c7f60cf861dac207caad47d79092df327a1fc1352ab7'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def atomic(p,o):
    p=Path(p);temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');write(temp,o);temp.replace(p)
def art(p):
    p=Path(p);a={'path':str(p),'sha256':sha(p)}
    if p.suffix.lower()=='.png':
        with Image.open(p) as im:a.update(size=list(im.size),format=im.format)
    return a
def check(a):assert sha(a['path'])==a['sha256'],a['path']
def rgb(a):check(a);return np.array(Image.open(a['path']).convert('RGB'))
def save(p,a):
    assert not Path(p).exists(),p
    (a if isinstance(a,Image.Image) else Image.fromarray(a)).save(p)
    return art(p)
def blend(base,m):
    check(m['native']);check(m['alpha'])
    with Image.open(m['native']['path']) as im:
        assert im.format=='PNG' and im.size==(1254,1254)
        native=np.array(im.convert('RGB').crop(m['nativeSourceCrop']))
    alpha=np.array(Image.open(m['alpha']['path']).convert('L'))[:,:,None]
    x0,y0,x1,y1=m['pasteBoxIn4096'];assert native.shape==base[y0:y1,x0:x1].shape and alpha.shape==native.shape[:2]+(1,)
    result=base.copy();old=result[y0:y1,x0:x1].copy()
    result[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-alpha)+native.astype(np.uint32)*alpha+127)//255).astype(np.uint8)
    return result
def replay_original(m):
    for k in ['sourceCandidate','sourceContext','immutableWest','native','generation','preparation','alpha','seamPaths','candidate','context']:check(m[k])
    gen=read(m['generation']['path']);check(gen['receipt']);assert read(gen['receipt']['path'])['status'].startswith('succeeded')
    result=blend(rgb(m['sourceCandidate']),m);assert np.array_equal(result,rgb(m['candidate']))
    ctx=rgb(m['sourceContext']);ctx[115:4211,115:4211]=result;assert np.array_equal(ctx,rgb(m['context']))
    return True

def build():
    authority=read(AUTH);assert authority['newArtworkGenerationAllowed'] and not authority['gitMutationsAllowedForProductionWorkers']
    frozen=read(FREEZE);selected=next(x for x in frozen['selectedCandidatePaths'] if x['tile']=='r13_c15')
    assert selected['candidate']['sha256']==BASE_SHA
    latest=read(T/'candidate/latest-assembly.json');assert latest['candidate']['sha256']==BASE_SHA
    checkpoint=read(CHECKPOINT);assert sha(CHECKPOINT)=='36cc00a482f84888cfe043447fe16c5315b0747045d2294277387094164a7698'
    version='unified-native-repairs-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    d=T/'repairs'/version;d.mkdir(exist_ok=False)
    review=T/'review'/version;review.mkdir(exist_ok=False)
    previous={}
    for name in ['progress.json','candidate/latest-assembly.json','selection.json']:
        p=T/name
        if p.exists():
            previous[name]=art(p);write(d/(name.replace('/','-')+'.before.json'),read(p))
    base=rgb(latest['candidate']);assert base.shape==(4096,4096,3)
    ctx=rgb(latest['context']);assert ctx.shape==(4326,4326,3)
    original=base.copy();result=base.copy();steps=[];union=np.zeros((4096,4096),dtype=bool)
    ornament=read(latest['manifest']['path']);check(latest['manifest'])
    protected=[]
    for item in ornament['steps']:
        x,y,_,_=item['tilePlacementBox'];l,t,r,b=item['alphaBounds'];protected.append([x+l,y+t,x+r,y+b])
    for i,entry in enumerate(checkpoint['stepsInReplayOrder'],1):
        for key in ['composition','qa','native','alpha','replay']:check(entry[key])
        assert read(entry['qa']['path'])['status']=='local_pass'
        comp=read(entry['composition']['path']);replay_original(comp)
        prior=result.copy();result=blend(result,comp);x0,y0,x1,y1=comp['pasteBoxIn4096'];union[y0:y1,x0:x1]=True
        for l,t,r,b in protected:assert np.array_equal(result[t:b,l:r],original[t:b,l:r])
        steps.append({**entry,'originalIndependentReplayExact':True,'inputPixelSha256':hashlib.sha256(prior.tobytes()).hexdigest(),'outputPixelSha256':hashlib.sha256(result.tobytes()).hexdigest(),'changedPixels':int(np.any(prior!=result,axis=2).sum())})
    assert not np.any(np.any(result!=original,axis=2)&~union)
    candidate=save(T/'candidate'/('r13_c15-4k-'+version+'.png'),result)
    write(d/'first-output.json',{'savedAtUtc':now(),'candidate':candidate,'actualNewNativeOutput':None,'nativeGenerationCalls':0,'kind':'new deterministic composition from already saved native sources'})
    print(json.dumps({'firstNewComposite':candidate,'version':version}),flush=True)
    ctx[115:4211,115:4211]=result;context=save(T/'candidate'/('r13_c15-context-4326-'+version+'.png'),ctx)
    checks=dict(originalIndependentReplaysExact=True,outsideThreePasteRectanglesUnchanged=True,ornamentProtectionBoxes=protected,ornamentPixelsUnchanged=True,immutableWestUnchanged=True,activeNativeMapUnchanged=True)
    manifest=dict(schemaVersion=1,tile='r13_c15',version=version,createdAtUtc=now(),status='unified_candidate_pending_visual_QA',formalAccepted=False,sourceCandidate=latest['candidate'],sourceContext=latest['context'],ornamentComposition=latest['manifest'],authority=art(AUTH),historicalFreeze=art(FREEZE),retainedCheckpoint=art(CHECKPOINT),stepsInReplayOrder=steps,immutableWest=checkpoint['immutableWest'],activeNativeMap=art(T/'active-native-map.json'),candidate=candidate,context=context,checks=checks,compositor=art(__file__),operation='Exact native crops and saved alpha; (base*(255-alpha)+native*alpha+127)//255 in uint32; no resizing or warping',newGenerationCalls=0,actualNewNativeOutput=None,resized=False,outerHalo='retained from selected ornament context; only4096 core replaced; not a reliable external geometry anchor',externalNeighborSeamQA='west_requires_current_visual_review; north/east/south pending',previousPointers=previous,reviewDirectory=str(review))
    write(d/'composition.json',manifest)
    replay=np.array(Image.open(latest['candidate']['path']).convert('RGB'))
    for step in steps:replay=blend(replay,read(step['composition']['path']))
    assert np.array_equal(replay,rgb(candidate));rc=rgb(latest['context']);rc[115:4211,115:4211]=replay;assert np.array_equal(rc,rgb(context));check(manifest['immutableWest']);check(manifest['historicalFreeze']);check(manifest['activeNativeMap'])
    write(d/'replay-verification.json',dict(verifiedAtUtc=now(),candidate=candidate,context=context,exactPixelReplay=True,checks=checks,formalAccepted=False))
    images=[]
    def crop(name,box):
        item=save(review/(name+'.png'),Image.fromarray(result).crop(box));images.append({**item,'cropBoxIn4096':box,'resized':False});return item
    for name,box in [('I1-table-rim',[2400,1260,3654,2514]),('I2-floor-leg',[225,2560,1479,3814]),('bell-protected',[1320,0,1920,480]),('cap-protected',[1960,3610,2660,4096])]:crop(name,box)
    west=rgb(checkpoint['immutableWest'])
    for k in range(4):
        y=k*1024;join=np.concatenate([west[y:y+1024,3696:4096],result[y:y+1024,0:400]],axis=1);item=save(review/f'west-{y}-{y+1024}-native.png',join);images.append({**item,'cropBoxIn4096':[-400,y,400,y+1024],'resized':False,'boundaryAtImageX':400})
    crop('W1-perimeter',[0,3260,950,4096])
    crop('south-new-joint',[0,3840,1100,4096])
    preview=Image.fromarray(result);preview.thumbnail((1024,1024));item=save(review/'overview-preview-only.png',preview);images.append({**item,'resized':True,'deliverable':False})
    write(review/'evidence.json',dict(candidate=candidate,west=checkpoint['immutableWest'],images=images))
    print(json.dumps({'manifest':str(d/'composition.json'),'review':str(review),'candidate':candidate,'context':context}),flush=True)

def publish(manifest_path,qa_path):
    m=read(manifest_path);qa=read(qa_path);check(m['candidate']);check(m['context']);assert qa['candidate']['sha256']==m['candidate']['sha256'] and qa['internalArtQA']=='local_pass'
    check(m['historicalFreeze']);check(m['activeNativeMap']);check(m['immutableWest'])
    latest=read(T/'candidate/latest-assembly.json');assert latest['candidate']['sha256']==BASE_SHA
    stamp=now();status='ornaments_and_structure_repaired_external_neighbors_pending'
    latest.update(updatedAtUtc=stamp,status=status,manifest=art(manifest_path),candidate=m['candidate'],context=m['context'],localVisualQA=str(qa_path),internalArtQA=qa['internalArtQA'],externalNeighborSeamQA=qa['externalNeighborSeamQA'],formalAccepted=False)
    progress=read(T/'progress.json');progress.update(updatedAt=stamp,status=status,candidate=m['candidate']['path'],candidateSha256=m['candidate']['sha256'],context=m['context']['path'],contextSha256=m['context']['sha256'],assemblyManifest=str(manifest_path),repairManifest=str(manifest_path),internalArtQA='local_pass',internalSeamQA='passed_after_native_repairs',externalNeighborSeamQA=qa['externalNeighborSeamQA'],localOrnamentQA='passed_preserved_exactly',localStructureQAReport=str(qa_path),formalAccepted=False,nextStep='Use current core-only borders for future north/east/south neighbors; south x0..629 includes new joint at x230. Retain west cosmetic wood-value watch; formal acceptance awaits external neighbors.')
    selection=dict(schemaVersion=1,tile='r13_c15',selectedAtUtc=stamp,status=status,candidate=m['candidate'],context=m['context'],manifest=art(manifest_path),visualQA=art(qa_path),activeNativeMap=m['activeNativeMap'],formalAccepted=False,source='three retained local-pass native repair recipes replayed onto selected ornament candidate')
    resume=dict(schemaVersion=1,tile='r13_c15',resumedAtUtc=m['createdAtUtc'],publishedAtUtc=stamp,authority=m['authority'],historicalFreeze=m['historicalFreeze'],historicalFreezeUnchanged=True,status=status,currentCoordinate='r13_c15',firstNewOutput=m['candidate'],firstNewNativeOutput=None,newGenerationCalls=0,inFlightImageGenCount=0,retainedNativeRepairCount=3,selectedCandidate=m['candidate'],selectedContext=m['context'],manifest=art(manifest_path),visualQA=art(qa_path),formalAccepted=False,remainingExternalQA=qa['externalNeighborSeamQA'],noGitOperations=True,noDeletion=True,noZoneProgressMutation=True,network='No request made; all work was offline reuse and exact composition.')
    atomic(T/'candidate/latest-assembly.json',latest);atomic(T/'progress.json',progress);atomic(T/'selection.json',selection);atomic(T/'production-resume-20261012.json',resume)
    write(Path(manifest_path).parent/'publication.json',dict(publishedAtUtc=stamp,pointers={name:art(T/name) for name in ['candidate/latest-assembly.json','progress.json','selection.json','production-resume-20261012.json']},formalAccepted=False))
    print(json.dumps(selection,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);s.add_parser('build');q=s.add_parser('publish');q.add_argument('manifest_path');q.add_argument('qa_path');a=vars(p.parse_args());cmd=a.pop('cmd');globals()[cmd](**a)
