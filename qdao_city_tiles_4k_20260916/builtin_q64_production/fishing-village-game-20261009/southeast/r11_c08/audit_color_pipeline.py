from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=read(T/'native-selected-before-color.json')
base=read(T/'shadow-s2-v1-selected.json')
final=read(T/'joint-edge-color-v1-selected.json')
jobs=[('S1-hull-shadow-v1',[30605,41605,31135,42500]),('S2-stone-shadow-v1',[32520,42740,32768,43360])]
records=[]
for pid,rel in base['patches'].items():
 src=T/rel;aa=np.asarray(Image.open(src).convert('RGB'),dtype=np.float32)
 fp=T/final['patches'][pid];result=np.asarray(Image.open(fp).convert('RGB'))
 nx=28672+(int(pid[2])-1)*1024-115;ny=40960+(int(pid[1])-1)*1024-115
 replay=aa.copy()
 if fp!=src:
  d=read(str(fp)+'.derivation.json');assert sha(src)==d['baseSha256']
  for f in d['fields']:
   assert sha(f['path'])==f['sha256'];field=np.load(f['path'])['additiveRgb'];b=f['globalBox']
   x,y,x1,y1=max(nx,b[0]),max(ny,b[1]),min(nx+1254,b[2]),min(ny+1254,b[3])
   if x<x1 and y<y1:replay[y-ny:y1-ny,x-nx:x1-nx]+=field[y-b[1]:y1-b[1],x-b[0]:x1-b[0]]
 replay=np.uint8(np.clip(np.rint(replay),0,255));assert np.array_equal(replay,result)
 anchor=np.asarray(Image.open(T/original['patches'][pid]).convert('RGB')).copy()
 for stem,b in jobs:
  jbox=read(T/'repairs'/f'{stem}.request.json')['globalBox'];joint=np.asarray(Image.open(T/'repairs'/f'{stem}.png').convert('RGB'))
  x,y,x1,y1=max(nx,b[0]),max(ny,b[1]),min(nx+1254,b[2]),min(ny+1254,b[3])
  if x<x1 and y<y1:anchor[y-ny:y1-ny,x-nx:x1-nx]=joint[y-jbox[1]:y1-jbox[1],x-jbox[0]:x1-jbox[0]]
 maximum=int(np.abs(result.astype(int)-anchor.astype(int)).max());assert maximum<=40
 records.append(dict(patch=pid,file=str(fp),sha256=sha(fp),jointFieldsReplayExactly=True,maxColorDeltaFromNativeGeometry=maximum))
out=T/'qa/shadow-final';out.mkdir(parents=True,exist_ok=True)
candidate=Image.open(out/'candidate-4096.png')
for stem,b in jobs:
 for edge,box in [('left',[b[0]-100,b[1],b[0]+100,b[3]]),('right',[b[2]-100,b[1],min(32768,b[2]+100),b[3]]),('top',[b[0],b[1]-100,b[2],b[1]+100]),('bottom',[b[0],b[3]-100,b[2],b[3]+100])]:
  candidate.crop((box[0]-28672,box[1]-40960,box[2]-28672,box[3]-40960)).save(out/f'{stem}-{edge}.png')
report=dict(tile='r11_c08',allJointFieldsReconstruct=True,geometryAnchor='Original native patches with exact generated joint crops substituted inside adoption boxes',maxColorDeltaFromNativeGeometry=max(r['maxColorDeltaFromNativeGeometry'] for r in records),records=records)
(T/'qa/color-pipeline-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='records'}))

