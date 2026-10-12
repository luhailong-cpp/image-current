"""Mechanical native core and current adjacency review crops; never repairs pixels."""
from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now,patch
import sys

revision=sys.argv[1]
qa=ROOT/'qa'/('r12_c11-sol-resume-20261012-'+revision)
assert not qa.exists(),'Use a fresh QA revision'
qa.mkdir()
sel=read(ROOT/'selection-r12_c11.json')['patchVersions']
im=Image.new('RGB',(4096,4096),(32,32,32));parts=[]
for rc,version in sorted(sel.items()):
    r,c=map(int,rc);f=ROOT/'native'/f'r12_c11_p{rc}_{version}.png'
    native=Image.open(f).convert('RGB');assert native.size==(1254,1254)
    core=native.crop((115,115,1139,1139));dest=((c-1)*1024,(r-1)*1024)
    im.paste(core,dest)
    assert np.array_equal(np.array(core),np.array(im.crop((dest[0],dest[1],dest[0]+1024,dest[1]+1024))))
    parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,1139],'destination':list(dest),'pixelExact':True})
missing=[str(r)+str(c) for r in range(1,5) for c in range(1,5) if str(r)+str(c) not in sel]
full=qa/'selected-core-board.png';im.save(full)
write(Path(str(full)+'.generation.json'),{'file':str(full),'sha256':sha(full),'generatedAt':now(),'operation':'unscaled exact core hard paste, no blend/warp/painting','contributions':parts,'missingCoordinates':missing,'unproducedRegions':'flat dark grey QA annotation, not artwork','usableAsFinalArt':not missing,'fullCoverage':not missing})
prev=qa/'selected-core-preview.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(prev)
write(Path(str(prev)+'.generation.json'),{'file':str(prev),'sha256':sha(prev),'source':str(full),'sourceSha256':sha(full),'operation':'downscaled QA preview only','usableAsFinalArt':False})
reports=[]
def seam(a,b,direction,name):
    a,b=Path(a),Path(b);ia=Image.open(a).convert('RGB');ib=Image.open(b).convert('RGB')
    if direction=='horizontal':
        abox=[883,0,1139,1254];bbox=[115,0,371,1254]
        out=Image.new('RGB',(512,1254));out.paste(ia.crop(abox),(0,0));out.paste(ib.crop(bbox),(256,0))
        x=np.array(ia)[:,1024:1254,:].astype(float);y=np.array(ib)[:,:230,:].astype(float)
    else:
        abox=[0,883,1254,1139];bbox=[0,115,1254,371]
        out=Image.new('RGB',(1254,512));out.paste(ia.crop(abox),(0,0));out.paste(ib.crop(bbox),(0,256))
        x=np.array(ia)[1024:1254,:,:].astype(float);y=np.array(ib)[:230,:,:].astype(float)
    f=qa/(name+'.png');out.save(f)
    rec={'file':str(f),'sha256':sha(f),'operation':'100-percent native hard crop at adjacent core boundary; no resizing or blending','direction':direction,'sources':[{'file':str(a),'sha256':sha(a),'sourceCrop':abox},{'file':str(b),'sha256':sha(b),'sourceCrop':bbox}],'overlapMAE':float(np.abs(x-y).mean()),'pixelExactOverlapFraction':float(np.all(x==y,axis=2).mean()),'status':'pending_visual_review'}
    write(Path(str(f)+'.generation.json'),rec);reports.append(rec)
for rc,ver in sorted(sel.items()):
    r,c=map(int,rc);a=ROOT/'native'/f'r12_c11_p{rc}_{ver}.png'
    for nr,nc,d in [(r,c+1,'horizontal'),(r+1,c,'vertical')]:
        key=str(nr)+str(nc)
        if key in sel:seam(a,ROOT/'native'/f'r12_c11_p{key}_{sel[key]}.png',d,rc+'-'+key)
    if r==1:
        nv={'1':'v02','2':'v01','3':'v02','4':'v01'}[str(c)]
        seam(ROOT/'native'/f'r11_c11_p4{c}_{nv}.png',a,'vertical','north-'+rc)
    if c==4:
        ev={'1':'v03','2':'v01','3':'v02','4':'v01'}[str(r)]
        seam(a,ROOT/'native'/f'r12_c12_p{r}1_{ev}.png','horizontal',rc+'-east')
write(qa/'manifest.json',{'tile':'r12_c11','generatedAt':now(),'selectedVersions':sel,'missingCoordinates':missing,'partialNativeCoreBoard':str(full),'preview':str(prev),'seams':reports,'formalAcceptedCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0})
print({'qa':str(qa),'seams':len(reports),'missing':missing})
