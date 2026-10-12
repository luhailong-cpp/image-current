from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1]
J=Z/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70'
paths={
 'r05_c04':J/'tiles/r05_c04-joint-4096.png',
 'r05_c05':J/'tiles/r05_c05-joint-4096.png',
 'r06_c04':J/'tiles/r06_c04-joint-4096.png',
 'r06_c05':J/'tiles/r06_c05-joint-4096.png',
 'r05_c06':Z/'r05_c06/candidate/r05_c06-candidate-minimum-error-03d4dd9f7332.png',
 'r06_c06':Z/'r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.png',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources=[{'tile':t,'file':str(p),'sha256':sha(p),'pasteXY':[(int(t[5:7])-4)*4096,(int(t[1:3])-5)*4096]} for t,p in paths.items()]
signature=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()[:16]
D=Z/'joint-six-tile-review'/signature
D.mkdir(parents=True,exist_ok=True)
imgs={t:Image.open(p).convert('RGB') for t,p in paths.items()}
def crop(box):
 out=Image.new('RGB',(box[2]-box[0],box[3]-box[1]))
 for s in sources:
  x,y=s['pasteXY']; left=max(x,box[0]);top=max(y,box[1]);right=min(x+4096,box[2]);bottom=min(y+4096,box[3])
  if left<right and top<bottom: out.paste(imgs[s['tile']].crop((left-x,top-y,right-x,bottom-y)),(left-box[0],top-box[1]))
 return out
entries=[]
def save(name,box,rot=False):
 im=crop(box)
 if rot: im=im.transpose(Image.Transpose.ROTATE_90)
 p=D/(name+'.png');im.save(p)
 entries.append({'file':str(p),'sha256':sha(p),'cropLTRB':box,'rotationCCW90':rot,'nativePixelScale':1,'sourceResampled':False,'actuallyViewed':False,'verdict':'pending'})
for part in range(8):
 y=part*1024
 save(f'east-boundary-x8192-segment{part+1:02}',[8192-160,y,8192+160,y+1024],True)
for part in range(4):
 x=8192+part*1024
 save(f'new-east-horizontal-y4096-segment{part+1:02}',[x,4096-160,x+1024,4096+160])
for y in range(1024,8192,1024): save(f'junction-x8192-y{y}',[8032,y-160,8352,y+160])
for x in range(9216,12288,1024): save(f'junction-x{x}-y4096',[x-160,3936,x+160,4256])
preview=Image.new('RGB',(1536,1024))
for s in sources: preview.paste(imgs[s['tile']].resize((512,512),Image.Resampling.LANCZOS),(s['pasteXY'][0]//8,s['pasteXY'][1]//8))
preview.save(D/'preview-only-1536.png')
index={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':sources,'qa':entries,'formalAccepted':False,'status':'external_candidate_edge_review_pending','previewOnly':str(D/'preview-only-1536.png'),'productionResampled':False,'script':{'file':str(Path(__file__)),'sha256':sha(Path(__file__))}}
(D/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print(json.dumps({'directory':str(D),'qaCount':len(entries),'sourceCount':len(sources)}))
