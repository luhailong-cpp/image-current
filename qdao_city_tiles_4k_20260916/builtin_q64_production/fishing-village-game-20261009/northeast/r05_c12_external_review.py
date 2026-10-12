import json
from pathlib import Path
from PIL import Image
import root_workflow as w
import r06_c14_extension as b
Z=w.Z;Q=Z/'qa'/'r05_c12-root-v2'/'external-neighbor-QA';Q.mkdir(exist_ok=True)
C=Z/'tiles'/'r05_c12.candidate-root-v2.png';assert b.sha(C)=='c1cc52322b48022a885146e66424e88461f2d3a685f63401f21dd66c0493ce33'
right={r:Z/'native'/f'r05_c13_p{r}1-{v}.png' for r,v in {1:'v2',2:'v3',3:'v4',4:'v3'}.items()}
pins={1:'a9cb502262869fd20a8050de8f0b26abf5a4cb25a909dcb0fb1a914bfdc4441b',2:'e1c1249087771f495501324c33352d3d399a8386fc26bc4e56ea5599b826d574',3:'15a2382c95faa9279fc5a4625e79eb4d7376e1f90968e883b686ec0f3c509976',4:'2b4b0ff800a83dc633ab17ed8c3213565dbfdddd542c64f5d9515de52c4b63f7'}
for r,p in right.items():assert b.sha(p)==pins[r]
def selected(tile,name):
 d=json.loads((Z/'records'/name).read_text(encoding='utf-8-sig'))['patches'];out={}
 for k,item in d.items():
  p=Path(item if isinstance(item,str) else item['path']);p=p if p.is_absolute() else Z/p
  if isinstance(item,dict):assert b.sha(p)==item['sha256']
  out[k]=p
 return out
south=selected('r06_c12','r06_c12.selection-closure-v5.json');se=selected('r06_c13','r06_c13.selection-proposed-v1.json')['r06_c13_p11'];items=[]
def qa(name,size,pieces):
 p=Q/(name+'.png');assert not p.exists();a=Image.new('RGB',size);src=[]
 for f,box,xy in pieces:
  im=Image.open(f).convert('RGB');a.paste(im.crop(box),xy);src.append(dict(b.ref(f,'native QA pixel source'),cropBox=box,pasteAt=xy))
 a.save(p);entry=dict(b.ref(p,'external native1:1 QA'),sources=src,pixels=list(size),operation='exact integer crop and opaque paste only; no resize, blend or paint',visualReview='pending',formalAccepted=False);w.atomic(str(p)+'.derived.json',entry);items.append(entry)
for r in range(1,5):
 y=(r-1)*1024;qa(f'right-segment-r{r}',(256,1024),[(C,[3968,y,4096,y+1024],[0,0]),(right[r],[115,115,243,1139],[128,0])])
for c in range(1,5):
 x=(c-1)*1024;qa(f'south-segment-c{c}',(1024,256),[(C,[x,3968,x+1024,4096],[0,0]),(south[f'r06_c12_p1{c}'],[115,115,1139,243],[0,128])])
for r in range(1,4):
 y=r*1024;qa(f'right-junction-r{r}',(512,512),[(C,[3840,y-256,4096,y+256],[0,0]),(right[r],[115,883,371,1139],[256,0]),(right[r+1],[115,115,371,371],[256,256])])
for c in range(1,4):
 x=c*1024;qa(f'south-junction-c{c}',(512,512),[(C,[x-256,3840,x+256,4096],[0,0]),(south[f'r06_c12_p1{c}'],[883,115,1139,371],[0,256]),(south[f'r06_c12_p1{c+1}'],[115,115,371,371],[256,256])])
qa('southeast-four-tile-junction',(512,512),[(C,[3840,3840,4096,4096],[0,0]),(right[4],[115,883,371,1139],[256,0]),(south['r06_c12_p14'],[883,115,1139,371],[0,256]),(se,[115,115,371,371],[256,256])])
w.atomic(Q/'manifest.json',{'createdAtUtc':b.now(),'candidate':b.ref(C,'r05_c12 candidate root-v2'),'qa':items,'formalAccepted':False,'visualReview':'pending','unavailableSides':['north owned neighbor incomplete','west transferred-zone seam not reviewed']});print(json.dumps({'qaCount':len(items),'directory':str(Q)}))
