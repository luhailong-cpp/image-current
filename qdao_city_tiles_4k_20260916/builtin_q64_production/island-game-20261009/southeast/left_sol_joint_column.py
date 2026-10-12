from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
import sys

def verify(f):
    r=read(Path(str(f)+'.generation.json'));assert sha(f)==r['sha256'] and sha(Path(r['prompt']))==r['promptSha256']
    for ref in r['references']:assert sha(Path(ref['file']))==ref['sha256']
    im=Image.open(f);assert im.size==(1254,1254) and im.mode=='RGB';return r

def upper_assemble():
    base=ROOT/'tiles/r12_c11.candidate-sol-20261012-v02.png';brec=read(Path(str(base)+'.generation.json'));assert sha(base)==brec['sha256']
    src=ROOT/'native/r12_c11_c12_shared_column_upper_v01.png';verify(src);assert sha(src)=='477f8e40d0e85dfd03294e99175a42274d77221681d70076df875d97961bf19c'
    crop=[330,750,620,1139];dest=[3799,3707,4089,4096];im=Image.open(base);im.paste(Image.open(src).crop(crop),tuple(dest[:2]));out=ROOT/'tiles/r12_c11.candidate-sol-20261012-v03.png';assert not out.exists();im.save(out)
    parts=brec['contributions']+[{'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest[:2],'destinationBox':dest,'record':str(src)+'.generation.json','ownership':'Final overlay of complete continuous lower shared column and surrounding water only; upper gold top and floor keep previous sources.'}]
    replay=np.zeros((4096,4096,3),dtype=np.uint8);ids=np.zeros((4096,4096),dtype=np.uint16)
    for i,p in enumerate(parts,1):
        assert sha(Path(p['file']))==p['sha256'];x,y,x2,y2=p['destinationBox'];replay[y:y2,x:x2]=np.asarray(Image.open(p['file']).crop(p['sourceCrop']));ids[y:y2,x:x2]=i
    assert np.array_equal(np.asarray(im),replay) and np.all(ids>0)
    for i,p in enumerate(parts,1):p['finalOwnedPixelCount']=int(np.count_nonzero(ids==i))
    folder=ROOT/'qa/r12_c11-sol-20261012-upper-v03';assert not folder.exists();folder.mkdir();Image.fromarray(ids).save(folder/'source-id.png')
    proof={'createdAt':now(),'candidate':str(out),'candidateSha256':sha(out),'operation':'Integer native crop and paste with explicit final source ownership. Original RGB pixels preserved.','sourceCount':17,'candidatePixelCount':4096*4096,'replayMismatchedPixels':0,'unownedPixels':0,'sourceIdMap':str(folder/'source-id.png'),'sourceIdMapSha256':sha(folder/'source-id.png'),'sources':parts};write(folder/'source-pixel-proof.json',proof)
    rec={**brec,'file':str(out),'sha256':sha(out),'generatedAt':now(),'operation':'Exact native core paste plus recorded native whole-column-region crop, no resize, blending, warping or painting','contributions':parts,'parentCandidate':str(base),'parentCandidateSha256':sha(base),'sourcePixelProof':str(folder/'source-pixel-proof.json'),'status':'candidate_pending_shared_column_overlay_edges_and_lower_continuation_review'};write(Path(str(out)+'.generation.json'),rec)
    entries=[]
    for name,box in [('top',[3671,3579,4096,3835]),('left',[3671,3707,3927,4096]),('right',[3961,3707,4096,4096]),('whole',[3549,3457,4096,4096])]:
        f=folder/(name+'.png');im.crop(box).save(f);entries.append({'id':name,'file':str(f),'sha256':sha(f),'sourceCrop':box,'status':'pending_visual_review'})
    write(folder/'overlay-edges.json',{'createdAt':now(),'candidate':str(out),'candidateSha256':sha(out),'sourceOverlay':{'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destinationBox':dest},'operation':'Exact candidate pixels, no resampling','entries':entries,'formalAccepted':False});print({'candidate':str(out),'sha256':sha(out),'sourceCount':17,'replayMismatchedPixels':0,'qa':str(folder)})

def lower_prepare():
    pid='r13_c11_c12_shared_column_lower';version='v01';guide=ROOT/'guides'/f'{pid}_{version}.png';promptfile=ROOT/'prompts'/f'{pid}_{version}.prompt.txt';requestfile=ROOT/'prompts'/f'{pid}_{version}.request.json';assert not any(f.exists() for f in [guide,promptfile,requestfile,ROOT/'native'/f'{pid}_{version}.png'])
    left=ROOT/'guides/r13_c11_p14.layout-only.png';right=ROOT/'native/r13_c12_p11_v02.png';upper=ROOT/'native/r12_c11_c12_shared_column_upper_v01.png';verify(upper);verify(right)
    im=Image.new('RGB',(1254,1254));im.paste(Image.open(left).crop((512,0,1254,1254)),(0,0));im.paste(Image.open(right).crop((115,0,742,1254)),(627,0));im.paste(Image.open(upper).crop((0,1024,1254,1254)),(0,0));im.save(guide)
    refs=[{'file':str(guide),'sha256':sha(guide),'role':'exact registered cross-column lower whole-object target; upper230 and rightcore are real sharp neighbors'}]+read(ROOT/'references.json')
    write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'createdAt':now(),'width':1254,'height':1254,'mode':'RGB','operation':'Mechanical unscaled source crop/paste into cross-column layout guide, reference only','usableAsFinalArt':False,'tile':'r13_c11','tileRelativeOrigin':[3469,-115],'globalBox':[44429,49037,45683,50291],'derivedFrom':[{'file':str(left),'sha256':sha(left),'sourceCrop':[512,0,1254,1254],'destination':[0,0]},{'file':str(right),'sha256':sha(right),'sourceCrop':[115,0,742,1254],'destination':[627,0]},{'file':str(upper),'sha256':sha(upper),'sourceCrop':[0,1024,1254,1254],'destination':[0,0]}]})
    prompt='''Use case: precise-object-edit.
Asset type: native 1254 x 1254 square close crop of one continuous wooden dock column and blue sea, daylight Q-painted Daoist game map.
Render the soft unfinished left-center interior of image 1 into matching crisp art. Image 1 is the exact registered coordinate target. Its top 230 pixels are the exact bottom of the already completed upper half of this same column. Keep that entire sharp top strip fixed. Continue the main column at x355..577 straight downward with the same width, wood grain, vertical contour and daylight shading. This lower half of the shared foreground column has no new ball or gold cap: the gold top is already above the frame. Follow the soft layout water foot around y1000, finishing this single continuous column once with a low rounded timber base at the waterline and a clear blue reflected shadow beneath. Preserve the exact column width and do not split it into pieces.
Keep the existing sharp right-side water and neighboring timber of image 1 fixed, including the clipped parts of the separate neighboring dock column at the far right. Keep the surrounding water broad rounded cyan-blue caustics at the existing scale, with delicate white ripples around the single main foot. Keep the close framing, scale and all object positions. Image 2 is full-map layout authority; image 3 is materials only; image 4 is painting style only. Output one opaque 1254 x 1254 square. No lettering, interface or watermark.
'''
    promptfile.write_text(prompt,encoding='utf-8');write(requestfile,{'promptPath':str(promptfile),'promptSha256':sha(promptfile),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'preparedAt':now(),'status':'prepared_not_submitted','tile':'r13_c11','tileRelativeOrigin':[3469,-115],'globalBox':[44429,49037,45683,50291]})
    print({'request':str(requestfile),'guide':str(guide)})

def lower_submit():
    pid='r13_c11_c12_shared_column_lower';f=ROOT/'prompts'/f'{pid}_v01.request.json';q=read(f);assert not (ROOT/'native'/f'{pid}_v01.png').exists();assert sha(Path(q['promptPath']))==q['promptSha256']
    for ref in q['references']:assert sha(Path(ref['file']))==ref['sha256']
    q.update(status='submitted_in_flight',submittedAt=now());write(f,q)
    for f in [ROOT/'progress-r13_c11.json',ROOT/'production-resume-left-sol-r13_c11-20261012.json']:
        p=read(f);p.update(updatedAt=now(),status='generating_shared_whole_column_lower',inFlightRequests=[{'patch':pid,'version':'v01','route':'builtin','submittedAt':q['submittedAt']}],currentPatch=pid,newGenerationAttempted=True);write(f,p)
    print({'submitted':pid+'_v01'})

def lower_receive(source):
    import shutil
    pid='r13_c11_c12_shared_column_lower';src=Path(source);out=ROOT/'native'/f'{pid}_v01.png';receipt=ROOT/'receipts'/f'{pid}_v01.json';request=ROOT/'prompts'/f'{pid}_v01.request.json';q=read(request)
    assert not out.exists() and not receipt.exists();im=Image.open(src);assert im.size==(1254,1254) and im.mode=='RGB';assert sha(Path(q['promptPath']))==q['promptSha256']
    for ref in q['references']:assert sha(Path(ref['file']))==ref['sha256']
    write(receipt,{'patchId':pid,'version':'v01','receivedAt':now(),'tool':'image_gen.imagegen','route':'builtin','status':'success','request':str(request),'requestSha256':sha(request),'promptPath':q['promptPath'],'promptSha256':q['promptSha256'],'references':q['references'],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativePixels':[1254,1254],'mode':'RGB','returnedFields':['image_url','output_hint'],'largeImageDataLogged':False,'actualModel':None,'actualQuality':None})
    shutil.copy2(src,out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'mode':'RGB','format':'PNG','tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'prompt':q['promptPath'],'promptSha256':q['promptSha256'],'references':q['references'],'evidence':{'toolReceipt':str(receipt),'returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'tile':'r13_c11','tileRelativeOrigin':[3469,-115],'globalBox':[44429,49037,45683,50291],'resizedAfterGeneration':False,'status':'candidate_pending_whole_column_and_north_outer_join_review'})
    for f in [ROOT/'progress-r13_c11.json',ROOT/'production-resume-left-sol-r13_c11-20261012.json']:
        p=read(f);p.update(updatedAt=now(),status='shared_whole_column_lower_received_pending_review',inFlightRequests=[],generatedNativeCount=len(list((ROOT/'native').glob('r13_c11_*.png'))),actualNativeCount=len(list((ROOT/'native').glob('r13_c11_*.png'))),lastNative=str(out),lastNativeSha256=sha(out),lastReceipt=str(receipt));write(f,p)
    folder=ROOT/'qa/r13_c11_c12-shared-lower-v01';assert not folder.exists();folder.mkdir();cand=ROOT/'tiles/r12_c11.candidate-sol-20261012-v03.png';a=Image.open(cand);join=Image.new('RGB',(290,512));join.paste(a.crop((3799,3840,4089,4096)),(0,0));join.paste(im.crop((330,115,620,371)),(0,256));jf=folder/'actual-north-join.png';join.save(jf);write(folder/'manifest.json',{'createdAt':now(),'target':str(out),'targetSha256':sha(out),'candidateNorth':str(cand),'candidateNorthSha256':sha(cand),'join':str(jf),'joinSha256':sha(jf),'northCandidateCrop':[3799,3840,4089,4096],'targetCrop':[330,115,620,371],'operation':'Exact source/candidate pixels and hard paste, no resampling','status':'pending_visual_review'});print({'native':str(out),'sha256':sha(out),'qa':str(folder)})

def row_prepare():
    folder=ROOT/'qa/r13_c11-first-row-sol-v01';assert not folder.exists();folder.mkdir();sel=read(ROOT/'selection-r13_c11.json')['patchVersions'];parts=[];row=Image.new('RGB',(4096,1024));ids=np.zeros((1024,4096),dtype=np.uint16)
    for c in range(1,5):
        rc='1'+str(c);f=ROOT/'native'/f'r13_c11_p{rc}_{sel[rc]}.png';verify(f);crop=[115,115,627 if c==4 else 1139,1139];dest=[(c-1)*1024,0,(c-1)*1024+(512 if c==4 else 1024),1024];row.paste(Image.open(f).crop(crop),tuple(dest[:2]));ids[:,dest[0]:dest[2]]=c;parts.append({'sourceId':c,'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destinationBox':dest})
    f=ROOT/'native/r13_c11_c12_shared_column_lower_v01.png';verify(f);crop=[115,115,627,1139];dest=[3584,0,4096,1024];row.paste(Image.open(f).crop(crop),tuple(dest[:2]));ids[:,3584:]=5;parts.append({'sourceId':5,'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destinationBox':dest})
    out=folder/'first-row.png';row.save(out);Image.fromarray(ids).save(folder/'source-id.png');replay=np.zeros((1024,4096,3),dtype=np.uint8)
    for p in parts:
        x,y,x2,y2=p['destinationBox'];replay[y:y2,x:x2]=np.asarray(Image.open(p['file']).crop(p['sourceCrop']));p['finalOwnedPixelCount']=int(np.count_nonzero(ids==p['sourceId']))
    assert np.array_equal(np.asarray(row),replay) and np.all(ids>0)
    entries=[]
    def save(name,im,info):
        f=folder/(name+'.png');im.save(f);entries.append({'id':name,'file':str(f),'sha256':sha(f),'status':'pending_visual_review',**info})
    for x in [1024,2048,3072,3584]:
        box=[x-256,0,x+256,1024];save('join-'+str(x),row.crop(box),{'sourceCrop':box,'source':str(out),'sourceSha256':sha(out)})
    north=ROOT/'tiles/r12_c11.candidate-sol-20261012-v03.png';n=Image.open(north)
    for c in range(4):
        im=Image.new('RGB',(1024,512));nb=[c*1024,3840,(c+1)*1024,4096];rb=[c*1024,0,(c+1)*1024,256];im.paste(n.crop(nb),(0,0));im.paste(row.crop(rb),(0,256));save('north'+str(c+1),im,{'neighbor':str(north),'neighborSha256':sha(north),'neighborCrop':nb,'source':str(out),'sourceSha256':sha(out),'sourceCrop':rb})
    east=ROOT/'native/r13_c12_p11_v02.png';e=Image.open(east);im=Image.new('RGB',(512,1024));im.paste(row.crop((3840,0,4096,1024)),(0,0));im.paste(e.crop((115,115,371,1139)),(256,0));save('actual-east',im,{'source':str(out),'sourceSha256':sha(out),'sourceCrop':[3840,0,4096,1024],'neighbor':str(east),'neighborSha256':sha(east),'neighborCrop':[115,115,371,1139]})
    write(folder/'manifest.json',{'createdAt':now(),'firstRow':str(out),'firstRowSha256':sha(out),'operation':'Exact native source crop and hard paste. Whole lower column and left sea floor meet at integer x3584. No blending.','pixelCount':4096*1024,'sourceCount':5,'replayMismatchedPixels':0,'sourceIdMap':str(folder/'source-id.png'),'sourceIdMapSha256':sha(folder/'source-id.png'),'sources':parts,'entries':entries,'fullyCovered4k':False,'formalAccepted':False});print({'qa':str(folder),'rowSha256':sha(out),'sources':5,'replayMismatchedPixels':0})

if sys.argv[1]=='upper-assemble':upper_assemble()
elif sys.argv[1]=='lower-prepare':lower_prepare()
elif sys.argv[1]=='lower-submit':lower_submit()
elif sys.argv[1]=='lower-receive':lower_receive(sys.argv[2])
elif sys.argv[1]=='row-prepare':row_prepare()
