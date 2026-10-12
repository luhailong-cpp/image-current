"""Independent local-only actual full-tile seams. Never changes production state."""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json,datetime

ROOT=Path(__file__).parent
FOLDER=ROOT/'qa/r11_c12-external-local-20261013'
assert not FOLDER.exists(), 'Preserve existing independent evidence'
FOLDER.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
paths={'candidate':ROOT/'tiles/r11_c12.candidate-v02.png','north':ROOT/'tiles/r10_c12.candidate-v02.png','west':ROOT/'tiles/r11_c11.candidate-v02.png','east':ROOT/'tiles/r11_c13.candidate-v02.png','south':ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png'}
ims={k:Image.open(p) for k,p in paths.items()}
for im in ims.values():assert im.size==(4096,4096) and im.mode=='RGB'
sources={k:{'file':str(p),'sha256':sha(p),'width':4096,'height':4096,'mode':'RGB'} for k,p in paths.items()}
entries=[]
def save(name,size,parts,kind,blank=None):
    im=Image.new('RGB',size,(120,120,120));replay=np.full((size[1],size[0],3),120,dtype=np.uint8);ownership=np.zeros((size[1],size[0]),dtype=np.uint8)
    specs=[]
    for sid,(key,box,dest) in enumerate(parts,1):
        crop=ims[key].crop(box);x,y=dest;w,h=crop.size;im.paste(crop,(x,y));replay[y:y+h,x:x+w]=np.asarray(crop);ownership[y:y+h,x:x+w]=sid
        specs.append({'sourceKey':key,**sources[key],'sourceCrop':box,'destination':dest,'sourcePixelCount':w*h,'identityMismatchedPixels':0})
    f=FOLDER/(name+'.png');im.save(f);actual=np.asarray(Image.open(f));mismatch=int(np.count_nonzero(np.any(actual!=replay,axis=2)));assert mismatch==0
    for sid,s in enumerate(specs,1):
        x,y=s['destination'];b=s['sourceCrop'];w,h=b[2]-b[0],b[3]-b[1];assert np.array_equal(actual[y:y+h,x:x+w],np.asarray(ims[s['sourceKey']].crop(b)))
    entries.append({'id':name,'kind':kind,'file':str(f),'sha256':sha(f),'width':size[0],'height':size[1],'operation':'Exact integer crop and hard paste of actual full candidates; no resampling or blend','identityMismatchedPixels':mismatch,'actualSourcePixelCount':int(np.count_nonzero(ownership)),'sources':specs,'blankReviewQuadrant':blank,'status':'pending_visual_review'})
for side in ['north','west','east','south']:
    for n in range(4):
        y=n*1024;x=y
        if side=='north':size=(1024,512);parts=[('north',[x,3840,x+1024,4096],[0,0]),('candidate',[x,0,x+1024,256],[0,256])]
        elif side=='south':size=(1024,512);parts=[('candidate',[x,3840,x+1024,4096],[0,0]),('south',[x,0,x+1024,256],[0,256])]
        elif side=='west':size=(512,1024);parts=[('west',[3840,y,4096,y+1024],[0,0]),('candidate',[0,y,256,y+1024],[256,0])]
        else:size=(512,1024);parts=[('candidate',[3840,y,4096,y+1024],[0,0]),('east',[0,y,256,y+1024],[256,0])]
        save(side+str(n+1),size,parts,'actual_external_seam')
corners={
 'northwest':[('candidate',[0,0,256,256],[256,256]),('north',[0,3840,256,4096],[256,0]),('west',[3840,0,4096,256],[0,256])],
 'northeast':[('candidate',[3840,0,4096,256],[0,256]),('north',[3840,3840,4096,4096],[0,0]),('east',[0,0,256,256],[256,256])],
 'southwest':[('candidate',[0,3840,256,4096],[256,0]),('south',[0,0,256,256],[256,256]),('west',[3840,3840,4096,4096],[0,0])],
 'southeast':[('candidate',[3840,3840,4096,4096],[0,0]),('south',[3840,0,4096,256],[0,256]),('east',[0,3840,256,4096],[256,0])]}
for name,parts in corners.items():save('corner-'+name,(512,512),parts,'actual_corner_three_cardinal_tiles','Gray quadrant is not artwork: diagonal tile outside assigned four-neighbor audit; no diagonal continuity claim.')
manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'left_resume_sol','task':'Independent r11_c12 actual full-tile four-side and corner local audit','sources':sources,'entryCount':len(entries),'externalSeamCount':16,'cornerCount':4,'sourcePixelIdentityMismatchCount':sum(e['identityMismatchedPixels'] for e in entries),'noGeneratedImages':True,'noFinalArtworkMutation':True,'noProductionStateMutation':True,'formalAccepted':False,'status':'all_exact_pixel_evidence_prepared_pending_visual_review','entries':entries}
write(FOLDER/'manifest.json',manifest)
print(json.dumps({'folder':str(FOLDER),'sources':sources,'entries':len(entries),'identityMismatchedPixels':0},ensure_ascii=False))
