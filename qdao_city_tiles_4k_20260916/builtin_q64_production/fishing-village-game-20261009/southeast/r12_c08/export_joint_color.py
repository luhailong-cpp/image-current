from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
J=T/'repairs/r12c08-rail-joint-v4.png';box=read(T/'repairs/r12c08-rail-joint-v4.request.json')['globalBox']
A=[32470,45066,32800,45491];fp=T/'processed/joint-edge-color-v1/r12c08-rail-joint-v4-edge-color-field.npz'
arr=np.asarray(Image.open(J).convert('RGB')).copy();original=arr.copy();field=np.load(fp)['additiveRgb']
x,y,x1,y1=A[0]-box[0],A[1]-box[1],A[2]-box[0],A[3]-box[1]
arr[y:y1,x:x1]=np.uint8(np.clip(np.rint(arr[y:y1,x:x1].astype(np.float32)+field),0,255))
out=T/'repairs/r12c08-rail-joint-v4-edge-color.png';Image.fromarray(arr).save(out)
write(str(out)+'.derivation.json',dict(file=str(out),sha256=sha(out),base=str(J),baseSha256=sha(J),globalBox=box,adoptionBox=A,colorField=str(fp),colorFieldSha256=sha(fp),maximumActualChannelCorrection=int(np.abs(arr.astype(int)-original.astype(int)).max()),operation='Exact generated joint plus bounded additive low-frequency field only inside adoption box',resampling=False,blur=False,blending=False))
s=read(T/'joint-edge-color-v1-selected.json');pp=T/s['patches']['p14'];p=np.asarray(Image.open(pp).convert('RGB'));base=np.asarray(Image.open(T/'native/p14-v2.png').convert('RGB')).copy()
nx,ny=31629,44941;bx,by,bx1,by1=max(nx,A[0]),max(ny,A[1]),min(nx+1254,A[2]),min(ny+1254,A[3])
base[by-ny:by1-ny,bx-nx:bx1-nx]=arr[by-box[1]:by1-box[1],bx-box[0]:bx1-box[0]]
assert np.array_equal(p,base)
write(T/'qa/rail-v4-local-adoption.json',dict(joint=str(out),sha256=sha(out),adoptionBox=A,p14=str(pp),p14Sha256=sha(pp),exactPixelReplay=True,geometry='Only rail adapter local rectangle checked; full p14 rejected pending wall G4/lower edge G5',promotedToSelected=False))
for path in [T/'rail-v4-selected.json',T/'joint-edge-color-v1-selected.json']:
 d=read(path);d.update(internalReady=False,formalAccepted=False,status='partial_candidate_with_known_geometry_defects',selectedCount=len(d['patches']),missing=['p42','p43','p44'],knownIssues=['G4 east wall crossing','G5 p14-p24 rock seam'],canvasMissingPixelsAreBlack=True);write(path,d)
 for candidate in [T/'processed/rail-v4/candidate-4096.png',T/'processed/joint-edge-color-v1/candidate-4096.png']:
  dp=Path(str(candidate)+'.derivation.json')
  d=read(dp) if dp.exists() else {}
  d.update(file=str(candidate),sha256=sha(candidate),classification='INCOMPLETE QA ASSEMBLY ONLY, 13 native cores; 3 missing cores black',nativeCoreCount=13,realPixelCoverage=13*1024*1024,formalAccepted=False,internalReady=False,operation='13 exact 1024 core crops; remaining canvas intentionally black');write(dp,d)
print(json.dumps(dict(correctedJoint=str(out),sha256=sha(out),maxActual=int(np.abs(arr.astype(int)-original.astype(int)).max()),replay=True)))

