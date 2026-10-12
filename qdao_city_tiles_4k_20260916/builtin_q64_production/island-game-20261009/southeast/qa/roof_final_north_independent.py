from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];Q=R/'qa/roof-final-north-independent';Q.mkdir(exist_ok=True)
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
n=R/'tiles/r08_c12.candidate-v15.png';s=R/'tiles/r09_c12.candidate-v08.png';b=R/'tiles/r09_c12.candidate-v06.png'
N=Image.open(n).convert('RGB');S=Image.open(s).convert('RGB');B=Image.open(b).convert('RGB');same=np.array_equal(np.asarray(S)[:256],np.asarray(B)[:256]);assert same
delta=np.any(np.asarray(S)!=np.asarray(B),axis=2);ys,xs=np.where(delta)
canvas=Image.new('RGB',(4096,512));canvas.paste(N.crop((0,3840,4096,4096)),(0,0));canvas.paste(S.crop((0,0,4096,256)),(0,256))
entries=[]
for i in range(4):
 box=[i*1024,0,(i+1)*1024,512];f=Q/f'north-{i+1}.png';canvas.crop(box).save(f)
 old=R/f'qa/roof-surface-v01/north-{i+1}.png'
 entries.append({'file':str(f),'sha256':sha(f),'northCrop':[i*1024,3840,(i+1)*1024,4096],'southCrop':[i*1024,0,(i+1)*1024,256],'sourcePixelsUnscaled':True,'pixelIdenticalToEarlierRoofSurfaceEvidence':Image.open(old).convert('RGB').tobytes()==Image.open(f).tobytes() if old.exists() else None})
junction=[]
for i in range(1,4):
 f=Q/f'junction-x{i*1024}.png';canvas.crop((i*1024-256,0,i*1024+256,512)).save(f);junction.append({'file':str(f),'sha256':sha(f),'nativeCropAroundTrueBoundary':True,'boundaryLocalXY':[256,256],'r09c12LocalX':i*1024})
report={'createdAt':datetime.now(timezone.utc).isoformat(),'reviewer':'coordinate_audit','sources':[{'file':str(p),'sha256':sha(p)} for p in [n,s,b]],'north256BandV08VsV06PixelExact':same,'north256ComparedPixels':4096*256,'v08VsV06ChangedBoundingBox':[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],'firstChangedRow':int(ys.min()),'r08Bottom256Unmodified':sha(n)=='ce6c1019f1df0bb3c327905fc696d7f266a812b295e3e3469786d58315ff5298','fourFullWidthSegments':entries,'threeRealBoundaryJunctions':junction,'priorEvidence':['qa/roof-surface-v01/review-index.json','qa/r08_c12-r09c12-final-split-proposal.json','qa/r08_c12.v15-final-review-evidence.json'],'status':'awaiting_direct_native_visual_review','formalAccepted':False}
wr(R/'qa/roof-final-north-independent.json',report)
print(json.dumps({k:v for k,v in report.items() if k not in ['sources','fourFullWidthSegments','threeRealBoundaryJunctions','priorEvidence']},indent=2))

