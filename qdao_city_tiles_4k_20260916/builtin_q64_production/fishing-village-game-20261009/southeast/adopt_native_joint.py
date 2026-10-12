"""Exact source-pixel adoption of a generated world joint, with replayable provenance."""
from pathlib import Path
from PIL import Image
import sys,json,hashlib
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
tile,selection,stem,outstem=sys.argv[1:5]
T=Z/tile
sel=read(T/selection)
joint=T/'repairs'/f'{stem}.png'
request=read(T/'repairs'/f'{stem}.request.json')
jbox=request.get('globalBox') or request['coordinate']['globalBox']
adopt=list(map(int,sys.argv[5:9])) if len(sys.argv)>5 else jbox
assert adopt[0]>=jbox[0] and adopt[1]>=jbox[1] and adopt[2]<=jbox[2] and adopt[3]<=jbox[3]
im=Image.open(joint).convert('RGB');assert im.size==(jbox[2]-jbox[0],jbox[3]-jbox[1])
ox=(int(tile[5:7])-1)*4096;oy=(int(tile[1:3])-1)*4096
D=T/'processed'/outstem;D.mkdir(parents=True,exist_ok=True)
sources=[]
for pid,rel in list(sel['patches'].items()):
 r,c=int(pid[1])-1,int(pid[2])-1
 nx,ny=ox+c*1024-115,oy+r*1024-115
 b=[max(nx,adopt[0]),max(ny,adopt[1]),min(nx+1254,adopt[2]),min(ny+1254,adopt[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 base=T/rel;img=Image.open(base).convert('RGB')
 crop=[b[0]-jbox[0],b[1]-jbox[1],b[2]-jbox[0],b[3]-jbox[1]]
 dest=[b[0]-nx,b[1]-ny]
 img.paste(im.crop(crop),dest)
 out=D/f'{pid}-{outstem}.png';img.save(out)
 write(out.with_suffix('.png.derivation.json'),{'file':str(out),'sha256':sha(out),'operation':'exact native generated joint crop adoption','base':str(base),'baseSha256':sha(base),'joint':str(joint),'jointSha256':sha(joint),'jointCrop':crop,'destination':dest,'globalAdoptionBox':adopt,'nativeDimensions':[1254,1254],'resamplingApplied':False,'warpApplied':False,'blurApplied':False,'blendApplied':False})
 sel['patches'][pid]=str(out.relative_to(T))
 sources.append(pid)
canvas=Image.new('RGB',(4096,4096));assembly=[]
for pid,rel in sel['patches'].items():
 r,c=int(pid[1])-1,int(pid[2])-1;p=T/rel
 canvas.paste(Image.open(p).crop((115,115,1139,1139)),(c*1024,r*1024))
 assembly.append({'patch':pid,'path':str(p),'sha256':sha(p),'crop':[115,115,1139,1139],'destination':[c*1024,r*1024]})
out=D/'candidate-4096.png';canvas.save(out)
write(out.with_suffix('.png.derivation.json'),{'file':str(out),'sha256':sha(out),'operation':'16 exact 1024 core crops','resamplingApplied':False,'layoutPixelsUsed':False,'sources':assembly})
sel['candidate']=str(out);sel['status']='joint_adoption_candidate_pending_QA';sel['internalReady']=False
write(T/f'{outstem}-selected.json',sel)
canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(D/'preview-QA-1024.png')
Q=T/'qa'/outstem;Q.mkdir(parents=True,exist_ok=True)
for label,b in [('left',[adopt[0]-128,adopt[1],adopt[0]+128,adopt[3]]),('right',[adopt[2]-128,adopt[1],adopt[2]+128,adopt[3]]),('top',[adopt[0],adopt[1]-128,adopt[2],adopt[1]+128]),('bottom',[adopt[0],adopt[3]-128,adopt[2],adopt[3]+128])]:
 b=[max(ox,b[0]),max(oy,b[1]),min(ox+4096,b[2]),min(oy+4096,b[3])]
 canvas.crop((b[0]-ox,b[1]-oy,b[2]-ox,b[3]-oy)).save(Q/f'{label}-adoption.png')
print(json.dumps({'selection':str(T/f'{outstem}-selected.json'),'candidate':str(out),'affectedPatches':sources}))
