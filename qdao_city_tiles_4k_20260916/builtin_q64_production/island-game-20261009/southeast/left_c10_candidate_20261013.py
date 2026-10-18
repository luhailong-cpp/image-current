from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
import sys

tile,revision,north_file,east_file=sys.argv[1:5]
assert tile in ['r13_c10','r14_c10']
sel=read(ROOT/f'selection-{tile}.json')['patchVersions'];assert set(sel)=={str(r)+str(c) for r in range(1,5) for c in range(1,5)}
out=ROOT/'tiles'/f'{tile}.candidate-{revision}.png';folder=ROOT/'qa'/f'{tile}-{revision}';assert not out.exists() and not folder.exists();folder.mkdir()
im=Image.new('RGB',(4096,4096));ids=np.zeros((4096,4096),dtype=np.uint16);coverage=np.zeros((4096,4096),dtype=np.uint8);parts=[]
def add(f,crop,box,role):
    f=Path(f);rec=read(Path(str(f)+'.generation.json'));assert sha(f)==rec['sha256'] and sha(Path(rec['prompt']))==rec['promptSha256']
    for ref in rec['references']:assert sha(Path(ref['file']))==ref['sha256']
    a=Image.open(f);assert a.size==(1254,1254) and a.mode=='RGB';x,y,x2,y2=box;px=a.crop(crop);assert px.size==(x2-x,y2-y);im.paste(px,(x,y));i=len(parts)+1;ids[y:y2,x:x2]=i;coverage[y:y2,x:x2]+=1;parts.append({'sourceId':i,'file':str(f),'sha256':sha(f),'record':str(f)+'.generation.json','sourceCrop':crop,'destinationBox':box,'destination':[x,y],'finalOwnedPixelCount':(x2-x)*(y2-y),'role':role,'sourcePromptAndReferenceHashesVerified':True})
for r in range(1,5):
    for c in range(1,5):
        rc=str(r)+str(c);x=(c-1)*1024;y=(r-1)*1024;split=tile=='r13_c11' and rc=='14';add(ROOT/'native'/f'{tile}_p{rc}_{sel[rc]}.png',[115,115,627 if split else 1139,1139],[x,y,x+(512 if split else 1024),y+1024],'selected patch native core; left half only when whole shared lower column owns right half')
        if split:add(ROOT/'native/r13_c11_c12_shared_column_lower_v01.png',[115,115,627,1139],[3584,0,4096,1024],'whole shared lower column core, exact source pixels')
assert np.all(coverage==1) and np.all(ids>0);im.save(out);Image.fromarray(ids).save(folder/'source-id.png');replay=np.zeros((4096,4096,3),dtype=np.uint8)
for p in parts:
    x,y,x2,y2=p['destinationBox'];replay[y:y2,x:x2]=np.asarray(Image.open(p['file']).crop(p['sourceCrop']))
mismatch=int(np.count_nonzero(np.any(np.asarray(im)!=replay,axis=2)));assert mismatch==0
proof={'createdAt':now(),'candidate':str(out),'candidateSha256':sha(out),'operation':'Replay exact original RGB native source core rectangles by integer crop and hard paste. No resize, paint, blending, warp or generated texture reuse.','sourceCount':len(parts),'candidatePixelCount':4096*4096,'coverageMin':int(coverage.min()),'coverageMax':int(coverage.max()),'replayMismatchedPixels':mismatch,'sourceIdMap':str(folder/'source-id.png'),'sourceIdMapSha256':sha(folder/'source-id.png'),'sources':parts,'actualModel':None,'actualQuality':None};write(folder/'source-pixel-proof.json',proof)
rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':4096,'height':4096,'mode':'RGB','operation':'Exact original native core rectangles hard pasted once per final pixel; no resize, blend, warp or painting','contributions':parts,'fullCoverage':True,'pixelCoverageMin':1,'pixelCoverageMax':1,'allContributionsPixelExact':True,'sourcePixelProof':str(folder/'source-pixel-proof.json'),'actualModel':None,'actualQuality':None,'status':'candidate_pending_actual_seam_junction_and_external_review'};write(Path(str(out)+'.generation.json'),rec)
entries=[]
def save(name,pixels,info):
    f=folder/(name+'.png');pixels.save(f);entries.append({'id':name,'file':str(f),'sha256':sha(f),'status':'pending_visual_review',**info})
def crop(name,box,kind):save(name,im.crop(box),{'kind':kind,'sourceCrop':box})
for r in range(4):
    for c in range(1,4):crop(f'h{r+1}{c}',[c*1024-256,r*1024,c*1024+256,(r+1)*1024],'internal')
for r in range(1,4):
    for c in range(4):crop(f'v{r}{c+1}',[c*1024,r*1024-256,(c+1)*1024,r*1024+256],'internal')
for r in range(1,4):
    for c in range(1,4):crop(f'j{r}{c}',[c*1024-256,r*1024-256,c*1024+256,r*1024+256],'junction')
if tile=='r13_c11':crop('whole-column-source-left-edge',[3328,0,3840,1024],'additional_source_join')
neighbors={}
for side,file in [('north',north_file),('east',east_file)]:
    if file=='none':continue
    f=Path(file);f=f if f.is_absolute() else ROOT/f;assert f.exists();a=Image.open(f);assert a.size==(4096,4096);neighbors[side]={'file':str(f),'sha256':sha(f)}
    for n in range(4):
        if side=='north':
            box=[n*1024,0,(n+1)*1024,256];nb=[n*1024,3840,(n+1)*1024,4096];pixels=Image.new('RGB',(1024,512));pixels.paste(a.crop(nb),(0,0));pixels.paste(im.crop(box),(0,256))
        else:
            box=[3840,n*1024,4096,(n+1)*1024];nb=[0,n*1024,256,(n+1)*1024];pixels=Image.new('RGB',(512,1024));pixels.paste(im.crop(box),(0,0));pixels.paste(a.crop(nb),(256,0))
        save(side+str(n+1),pixels,{'kind':'external','candidateCrop':box,'neighbor':str(f),'neighborSha256':sha(f),'neighborCrop':nb})
if east_file=='none':
    east=tile.replace('c10','c11');selection=ROOT/f'selection-{east}.json'
    if selection.exists():
        es=read(selection)['patchVersions']
        for r in range(1,5):
            key=str(r)+'1'
            if key not in es:continue
            f=ROOT/'native'/f'{east}_p{key}_{es[key]}.png';a=Image.open(f);box=[3840,(r-1)*1024,4096,r*1024];nb=[115,115,371,1139];pixels=Image.new('RGB',(512,1024));pixels.paste(im.crop(box),(0,0));pixels.paste(a.crop(nb),(256,0));save('east-native'+str(r),pixels,{'kind':'external_selected_native','candidateCrop':box,'neighbor':str(f),'neighborSha256':sha(f),'neighborCrop':nb,'note':'Final east candidate must confirm this boundary once assembled.'})
write(folder/'seams-junctions-external.json',{'createdAt':now(),'candidate':str(out),'candidateSha256':sha(out),'operation':'Exact original candidate pixels and actual neighbor hard joins, no resampling','internalSeamCount':24,'junctionCount':9,'entries':entries,'neighbors':neighbors,'formalAccepted':False})
preview=folder/'preview.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(preview);write(Path(str(preview)+'.generation.json'),{'file':str(preview),'sha256':sha(preview),'operation':'Downscaled review only; never final artwork','source':str(out),'sourceSha256':sha(out)})
for f in [ROOT/f'progress-{tile}.json',ROOT/f'production-resume-left-sol-{tile}-20261012.json']:
    p=read(f);p.update(updatedAt=now(),status='fully_covered_actual_candidate_pending_qa',candidate=str(out),candidateSha256=sha(out),sourcePixelProof=str(folder/'source-pixel-proof.json'),usedSourceCount=len(parts),fullyCovered4kCount=1,internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,nextStep='View24actual seams9junctions and available external sides; independent root review then continue next row.');write(f,p)
print({'candidate':str(out),'sha256':sha(out),'sources':len(parts),'replayMismatchedPixels':0,'qa':str(folder)})
