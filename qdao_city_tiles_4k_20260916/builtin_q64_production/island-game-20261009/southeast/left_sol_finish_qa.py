from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT, read, write, sha, now

def root_review():
    manifest=read(ROOT/'qa/r12_c12-sol-20261012-v01/seams.json')
    out=ROOT/'root-candidate-independent-review.json'
    assert not out.exists()
    candidate=Path(manifest['candidate']);assert sha(candidate)==manifest['candidateSha256']
    art=Image.open(candidate)
    entries=[]
    for e in manifest['entries']:
        assert sha(Path(e['file']))==e['sha256']
        assert np.array_equal(np.asarray(art.crop(e['sourceCrop'])),np.asarray(Image.open(e['file'])))
        entries.append({**e,'status':'independent_visual_pass_no_substantive_issue','actualCandidatePixelsVerified':True})
    assert len(entries)==24
    write(out,{'createdAt':now(),'reviewer':'left_resume_sol','candidate':str(candidate),'candidateSha256':sha(candidate),'scope':'24 exact candidate internal seams at 100 percent, independent visual review; junctions and external edges are root reviewer scope','reviewedSeamCount':24,'allCropHashesAndActualPixelsVerified':True,'entries':entries,'actionableIssues':[],'observations':'Timber rails, diagonal beams, step outlines and post silhouettes continue through actual seams. Fine wood grain and water phase variations do not require regeneration.','internalIndependentReviewPassed':True,'formalAccepted':False})
    print({'review':str(out),'independentSeamsPassed':24})

def own_prepare():
    candidate=ROOT/'tiles/r12_c11.candidate-sol-20261012-v02.png'
    rec=read(Path(str(candidate)+'.generation.json'));assert sha(candidate)==rec['sha256']
    out=ROOT/'qa/r12_c11-sol-20261012-final-v02';assert not out.exists();out.mkdir()
    art=Image.open(candidate);a=np.asarray(art);ids=np.zeros((4096,4096),dtype=np.uint16);replay=np.zeros_like(a);coverage=np.zeros((4096,4096),dtype=np.uint8);sources=[]
    for i,c in enumerate(rec['contributions'],1):
        f=Path(c['file']);assert sha(f)==c['sha256']
        im=Image.open(f);assert im.size==(1254,1254) and im.mode=='RGB'
        x,y,x2,y2=c['destinationBox'];px=np.asarray(im.crop(c['sourceCrop']))
        assert px.shape==(y2-y,x2-x,3)
        replay[y:y2,x:x2]=px;ids[y:y2,x:x2]=i;coverage[y:y2,x:x2]+=1
        sources.append({'sourceId':i,**c,'pixelCount':int(px.shape[0]*px.shape[1]),'sourceHashVerified':True})
    mismatch=int(np.count_nonzero(np.any(a!=replay,axis=2)))
    assert mismatch==0 and int(coverage.min())==1 and int(coverage.max())==1
    Image.fromarray(ids).save(out/'source-id.png')
    write(out/'source-pixel-proof.json',{'createdAt':now(),'candidate':str(candidate),'candidateSha256':sha(candidate),'operation':'Replay every original native RGB source core by integer crop and hard paste. Full candidate comparison, no resize or blending.','sourceCount':len(sources),'candidatePixelCount':4096*4096,'coverageMin':1,'coverageMax':1,'replayMismatchedPixels':mismatch,'sourceIdMap':str(out/'source-id.png'),'sourceIdMapSha256':sha(out/'source-id.png'),'sources':sources,'actualModel':None,'actualQuality':None})
    entries=[]
    def crop(name,box,kind):
        f=out/(name+'.png');art.crop(box).save(f);entries.append({'id':name,'kind':kind,'file':str(f),'sha256':sha(f),'sourceCrop':box,'status':'pending_visual_review'})
    for r in range(4):
        for c in range(1,4):crop(f'h{r+1}{c}',[c*1024-256,r*1024,c*1024+256,(r+1)*1024],'internal_horizontal')
    for r in range(1,4):
        for c in range(4):crop(f'v{r}{c+1}',[c*1024,r*1024-256,(c+1)*1024,r*1024+256],'internal_vertical')
    for r in range(1,4):
        for c in range(1,4):crop(f'j{r}{c}',[c*1024-256,r*1024-256,c*1024+256,r*1024+256],'junction')
    for edge,file in [('north','tiles/r11_c11.candidate-v02.png'),('east','tiles/r12_c12.candidate-sol-20261012-v01.png')]:
        f=ROOT/file;neighbor=Image.open(f);assert neighbor.size==(4096,4096)
        for n in range(4):
            if edge=='north':
                box=[n*1024,0,(n+1)*1024,256];nb=[n*1024,3840,(n+1)*1024,4096];im=Image.new('RGB',(1024,512));im.paste(neighbor.crop(nb),(0,0));im.paste(art.crop(box),(0,256))
            else:
                box=[3840,n*1024,4096,(n+1)*1024];nb=[0,n*1024,256,(n+1)*1024];im=Image.new('RGB',(512,1024));im.paste(art.crop(box),(0,0));im.paste(neighbor.crop(nb),(256,0))
            target=out/f'{edge}{n+1}.png';im.save(target);entries.append({'id':f'{edge}{n+1}','kind':'external','file':str(target),'sha256':sha(target),'candidateCrop':box,'neighbor':str(f),'neighborSha256':sha(f),'neighborCrop':nb,'status':'pending_visual_review'})
    write(out/'seams-junctions-external.json',{'createdAt':now(),'candidate':str(candidate),'candidateSha256':sha(candidate),'operation':'Exact original candidate pixels, no resampling, plus north/east actual candidate hard joins','internalSeamCount':24,'junctionCount':9,'externalSegmentCount':8,'entries':entries,'formalAccepted':False})
    print({'qa':str(out),'sourceCount':len(sources),'replayMismatchedPixels':mismatch,'internalSeams':24,'junctions':9,'externalSegments':8})

def own_finish():
    folder=ROOT/'qa/r12_c11-sol-20261012-final-v02';m=read(folder/'seams-junctions-external.json');candidate=Path(m['candidate']);assert sha(candidate)==m['candidateSha256']
    for e in m['entries']:
        assert sha(Path(e['file']))==e['sha256'];e['status']='visual_pass_no_substantive_issue'
    m.update({'reviewedAt':now(),'reviewer':'left_resume_sol','internalSeamsPassed':24,'junctionsPassed':9,'availableExternalSegmentsPassed':8,'availableExternalSidesPassed':['north','east'],'unavailableNeighborSides':['west','south'],'observations':'Rail, stair and pillar contours are connected. Fine wood grain and water phase variations retained; no substantive seam geometry failure.','sourcePixelProof':str(folder/'source-pixel-proof.json'),'formalAccepted':False,'formalAcceptancePending':'Independent root review and future external neighbors as available.'});write(folder/'left-visual-review.json',m)
    selected=read(ROOT/'selection-r12_c11.json')['patchVersions'];inventory=[]
    for f in sorted((ROOT/'native').glob('r12_c11_*.png')):
        r=read(Path(str(f)+'.generation.json'));assert sha(f)==r['sha256'] and sha(Path(r['prompt']))==r['promptSha256']
        for ref in r['references']:assert sha(Path(ref['file']))==ref['sha256']
        rc=f.stem.split('_p')[1][:2];ver=f.stem.rsplit('_',1)[1]
        inventory.append({'file':str(f),'sha256':sha(f),'generationRecord':str(Path(str(f)+'.generation.json')),'width':r['width'],'height':r['height'],'selected':selected.get(rc)==ver,'generationRecordHashMatches':True,'promptHashMatches':True,'referenceHashesMatch':True,'status':r['status']})
    p=read(ROOT/'progress-r12_c11.json');p.update({'updatedAt':now(),'status':'complete_core_internal_and_available_external_passed_pending_independent_review','generatedNativeCount':len(inventory),'selectedCoordinateCount':16,'selectedVersions':selected,'nativeInventory':inventory,'fullyCovered4kCount':1,'internalPassed4kCount':1,'externalPassed4kCount':0,'availableExternalSidesPassed':['north','east'],'unavailableNeighborSides':['west','south'],'formalAcceptedCount':0,'inFlightRequests':[],'candidate':str(candidate),'candidateSha256':sha(candidate),'visualReview':str(folder/'left-visual-review.json'),'sourcePixelProof':str(folder/'source-pixel-proof.json'),'lastRejectedNative':'r12_c11_p31_v02.png','nextStep':'Continue r13_c11 using this passed r12 south boundary as exact north anchor; independent root review remains open.'});write(ROOT/'progress-r12_c11.json',p)
    resume=read(ROOT/'production-resume-left-sol-20261012.json');assert sha(ROOT/'migration-freeze-left-20261011.json')==resume['historicalFreezeSha256'];resume.update({'updatedAt':now(),'status':p['status'],'actualNativeCount':len(inventory),'selectedVersions':selected,'selectedCoordinateCount':16,'missingCoordinates':[],'nativeInventory':inventory,'fullyCovered4kCount':1,'internalPassed4kCount':1,'externalPassed4kCount':0,'formalAcceptedCount':0,'candidate':str(candidate),'candidateSha256':sha(candidate),'visualReview':p['visualReview'],'sourcePixelProof':p['sourcePixelProof'],'lastRejectedNative':p['lastRejectedNative'],'nextStep':p['nextStep'],'inFlightRequests':[]});write(ROOT/'production-resume-left-sol-20261012.json',resume)
    print({'candidate':str(candidate),'sha256':sha(candidate),'internalPassed':24,'junctionsPassed':9,'availableExternalSidesPassed':['north','east'],'nativeCount':len(inventory),'formalAccepted':False})

if __name__=='__main__':
    import sys
    if sys.argv[1]=='root-review':root_review()
    elif sys.argv[1]=='own-prepare':own_prepare()
    elif sys.argv[1]=='own-finish':own_finish()
