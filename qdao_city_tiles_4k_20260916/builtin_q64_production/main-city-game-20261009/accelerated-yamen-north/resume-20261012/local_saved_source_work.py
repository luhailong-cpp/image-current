"""Native pixel reuse trial only. No image synthesis, resize, warp or spatial blur."""
import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;OUT=HERE/'d4-narrow-reuse-v1';OUT.mkdir(exist_ok=True)
basefile=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png';tile=np.array(Image.open(basefile).convert('RGB'));base=tile[2400:3654,1695:4096].copy()
f1=ROOT/'continuation-20261011/roof-row01/raw-v1.png';f2=ROOT/'continuation-20261011/roof-row02/raw-v1.png';a=np.array(Image.open(f1).convert('RGB'));b=np.array(Image.open(f2).convert('RGB'));gen=base.copy();gen[:,:1254]=a;gen[:,1147:]=b
sid=np.ones((1254,2401),np.uint8);sid[:,1147:]=2
path=p.minimum_seam(a[480:650,1147:],b[480:650,:107]);path=np.pad(path,(480,604),mode='edge')
for y in range(1254):
 k=1147+path[y];gen[y,1147:k]=a[y,1147:k];sid[y,1147:k]=1
y,x=np.indices((1254,2401))
top=p.minimum_seam(base[490:535].transpose(1,0,2),gen[490:535].transpose(1,0,2))+490
bottom=p.minimum_seam(base[605:632].transpose(1,0,2),gen[605:632].transpose(1,0,2))+605
# Larger left correction returns beneath the occluding golden curl; right uses a narrow material return.
bottom[:580]=np.maximum(bottom[:580],730)
m=(y>=top[None,:])&(y<bottom[None,:])&(x>=205)
gold=(base[:,:,0]>140)&(base[:,:,1]>85)&(base[:,:,2]<130)&(base[:,:,0]>base[:,:,2]*1.4)
m[gold]=False
final=base.copy();final[m]=gen[m]
p.save_png(OUT/'derived-strip-native.png',Image.fromarray(final));p.save_png(OUT/'binary-support.png',Image.fromarray(m.astype('uint8')*255));p.save_png(OUT/'source-index.png',Image.fromarray(sid))
p.put_json(OUT/'derivation.json',{'createdAt':p.now(),'status':'local saved-source assembly trial pending view; not adopted','baseFile':str(basefile),'baseSHA256':p.sha(basefile),'tileBox':[1695,2400,4096,3654],'sources':[p.reference(f1,'saved builtin source1 at strip x0'),p.reference(f2,'saved builtin source2 at strip x1147')],'support':p.reference(OUT/'binary-support.png','binary source copy support'),'sourceIndex':p.reference(OUT/'source-index.png','source at identical coordinates'),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'method':'Copy existing source pixels at identical world coordinates, protect original gold pixels. No new generation, blend, resize, warp or blur.','nativeSingleGenerationClaim':False,'formalAccepted':False})
for i,(l,r) in enumerate([(130,950),(900,1650),(1600,2401)],1):p.save_png(OUT/f'qa-native-{i}.png',Image.fromarray(final).crop((l,460,r,760)))
# Fresh exact contexts for unsolved defects; preparation only, never treated as generated output.
contexts=[('r03_c05','d1-left',[0,430,1254,1684]),('r03_c05','d1-right',[1100,430,2354,1684]),('r04_c04','rail-facet',[300,2400,1554,3654])]
sources=p.read(ROOT/'continuation-20261011/checkpoint-v2/sources.json');prepared=[]
for coord,name,box in contexts:
 d=HERE/'prepared-contexts'/name;d.mkdir(parents=True,exist_ok=True);f=Path(sources[coord]['file']);im=Image.open(f).crop(box);rec=p.save_png(d/'context-native.png',im);p.put_json(d/'preparation.json',{'tile':coord,'baseCandidate':str(f),'baseSHA256':p.sha(f),'tileBox':box,'pixels':[1254,1254],'operation':'Exact native crop only; no generated pixels','status':'prepared_not_submitted','context':rec});prepared.append(str(d/'preparation.json'))
print({'localTrial':str(OUT),'preparedContextCount':len(prepared),'newGeneratedOutputCount':0})

