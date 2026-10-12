from pathlib import Path
from PIL import Image
import hashlib,json,io,datetime
import numpy as np
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pngsha(im):
    buf=io.BytesIO();im.save(buf,format='PNG');return hashlib.sha256(buf.getvalue()).hexdigest()
base=T/'candidate'/'r13_c13-4k-candidate.png';current=T/'candidate'/'r13_c13-4k-candidate-repaired.png'
assembly=read(T/'candidate'/'assembly-manifest.json');assert sha(base)==assembly['output']['sha256']
history=read(R/'composition-history.json');im=Image.open(base).convert('RGB');state_sha=sha(base);steps=[]
for step in history['steps']:
    id=step['id'];assert state_sha==step['sourceSha256']
    native=Path(step['native']);assert sha(native)==step['nativeSha256']
    rec=read(R/f'{id}-native.png.generation.json');assert rec['sha256']==sha(native) and rec['width']==rec['height']==1254
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    req=read(rec['evidence']['request']);receipt=read(rec['evidence']['receipt']);assert receipt['status'].startswith('succeeded')
    prompt=Path(rec['prompt']);assert sha(prompt)==rec['promptSha256'] and req['prompt']==prompt.read_text(encoding='utf-8')
    for ref in rec['references']:
        assert sha(ref['path'])==ref['sha256']
        assert list(Image.open(ref['path']).size)==ref['dimensions']
    meta=rec['targetMetadata'];target=Image.open(meta['target']).convert('RGB');box=step['placement']
    assert sha(meta['target'])==meta['targetSha256']
    assert np.array_equal(np.asarray(im.crop(box)),np.asarray(target)),id+' target crop mismatch'
    mask=Path(step['mask']);assert sha(mask)==step['maskSha256']
    p=Image.open(native).convert('RGB');assert p.size==target.size==(1254,1254)
    im.paste(Image.composite(p,im.crop(box),Image.open(mask)),(box[0],box[1]))
    state_sha=pngsha(im);assert state_sha==step['outputSha256'],id+' replay hash mismatch'
    steps.append({'id':id,'sourceNativeSize':[1254,1254],'referencesVerified':True,'requestPromptVerified':True,'replayedOutputSha256':state_sha,'exactReplay':True})
context_path=R/'context-composition.json'
context_output=None
if context_path.exists():
    step=read(context_path);rec=read(step['generationRecord']);id=step['id']
    req=read(rec['evidence']['request']);receipt=read(rec['evidence']['receipt'])
    assert receipt['status'].startswith('succeeded')
    assert rec['actualModel'] is None and rec['actualQuality'] is None
    assert sha(rec['prompt'])==rec['promptSha256'] and req['prompt'].rstrip('\r\n')==Path(rec['prompt']).read_text(encoding='utf-8').rstrip('\r\n')
    for ref in rec['references']:
        assert sha(ref['path'])==ref['sha256'] and list(Image.open(ref['path']).size)==ref['dimensions']
    derive=step['sourceDerivation'];assert state_sha==derive['currentCoreSha256']
    assert sha(derive['baseContext'])==derive['baseContextSha256']
    ctx=Image.open(derive['baseContext']).convert('RGB');ctx.paste(im,(115,115))
    assert pngsha(ctx)==step['sourceSha256']==sha(step['source'])
    box=step['placementIn4326'];meta=rec['targetMetadata']
    assert sha(meta['target'])==meta['targetSha256']
    assert np.array_equal(np.asarray(ctx.crop(box)),np.asarray(Image.open(meta['target']).convert('RGB')))
    assert sha(step['native'])==step['nativeSha256']==rec['sha256']
    p=Image.open(step['native']).convert('RGB');assert p.size==(1254,1254)
    assert sha(step['mask'])==step['maskSha256']
    ctx.paste(Image.composite(p,ctx.crop(box),Image.open(step['mask'])),(box[0],box[1]))
    assert pngsha(ctx)==step['outputContextSha256']==sha(step['outputContext'])
    im=ctx.crop(step['finalCropBox']);state_sha=pngsha(im)
    assert state_sha==step['outputCoreSha256']
    context_output={'file':step['outputContext'],'sha256':step['outputContextSha256'],'size':[4326,4326],'formalCoreMatches':True,'externalSeamsVerified':False}
    steps.append({'id':id,'sourceNativeSize':[1254,1254],'referencesVerified':True,'requestPromptVerified':True,'replayedOutputSha256':state_sha,'replayedContextSha256':step['outputContextSha256'],'exactReplay':True})
assert state_sha==sha(current) and Image.open(current).size==(4096,4096)
recs=list((T/'native').glob('*.generation.json'))
report={'verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':str(current),'sha256':state_sha,'size':[4096,4096],'coreNativeSources':16,'nativePatchGeneratedCount':len(recs),'nativeRepairGeneratedCount':len(steps),'allGeneratedNativeCount':len(recs)+len(steps),'resampledArt':False,'modelQualityActual':{'model':None,'quality':None,'note':'Tool did not disclose actual values; config targets do not establish backend version.'},'repairSteps':steps,'formalAccepted':False,'externalSeamsVerified':False,'status':'provenance_and_exact_pixel_replay_verified_visual_qa_separate'}
report['contextOutput']=context_output
(T/'candidate'/'replay-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
pr=read(B/'progress.json');pr.update(updatedAt=report['verifiedAt'],status='candidate_final_internal_review',generatedNativeCount=report['allGeneratedNativeCount'],nativePatchGeneratedCount=len(recs),nativeRepairCount=len(steps),activeNativePatchCount=16,complete4kCandidateCount=1,formalAcceptedCount=0,provenanceVerified=True,exactReplayVerified=True,nextStep='Review six native repair perimeters at100%; retain candidate as non-formal until internal geometry and neighboring tile seam checks pass.')
(B/'progress.json').write_text(json.dumps(pr,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidate':str(current),'sha256':state_sha,'size':[4096,4096],'coreNativeSourceCount':16,'nativeRepairCount':len(steps),'allGeneratedNativeCount':len(recs)+len(steps),'exactReplay':True,'formalAccepted':False}))

