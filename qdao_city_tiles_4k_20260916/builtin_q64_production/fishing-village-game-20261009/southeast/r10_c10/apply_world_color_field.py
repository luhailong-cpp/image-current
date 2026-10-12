"""Apply a saved additive field in world coordinates; never copy another patch's picture."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
T=Path(__file__).resolve().parent
pid,field_rel,tag=sys.argv[1:4];rect=list(map(int,sys.argv[4:8]));bases=dict(a.split('=',1) for a in sys.argv[8:])
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
coords={p['id']:p['globalBox'] for p in read(T/'coordinate-plan.json')['patches']}
gb=coords[pid];world=[gb[0]+rect[0],gb[1]+rect[1],gb[0]+rect[2],gb[1]+rect[3]]
fp=T/field_rel;field=np.load(fp)['additiveField'];sel=read(T/'selected-patches.json');records=[]
for key,restore_rel in bases.items():
 pb=coords[key];b=[max(pb[0],world[0]),max(pb[1],world[1]),min(pb[2],world[2]),min(pb[3],world[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 current=T/sel['patches'][key];restore=T/restore_rel
 a=np.asarray(Image.open(current).convert('RGB')).copy();original=a.copy();r=np.asarray(Image.open(restore).convert('RGB'),dtype=np.float32)
 sx0,sy0,sx1,sy1=b[0]-gb[0],b[1]-gb[1],b[2]-gb[0],b[3]-gb[1]
 x0,y0,x1,y1=b[0]-pb[0],b[1]-pb[1],b[2]-pb[0],b[3]-pb[1]
 delta=field[sy0:sy1,sx0:sx1];a[y0:y1,x0:x1]=np.uint8(np.clip(np.rint(r[y0:y1,x0:x1]+delta),0,255))
 out=T/'processed'/f'{key}-{tag}.png';assert not out.exists();Image.fromarray(a).save(out)
 mask=np.ones((1254,1254),bool);mask[y0:y1,x0:x1]=False;assert np.array_equal(a[mask],original[mask])
 rec={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'base':{'path':str(current),'sha256':sha(current)},'geometryPixelSourceInRegion':{'path':str(restore),'sha256':sha(restore)},'worldRegion':b,'nativeRegion':[x0,y0,x1,y1],'field':{'path':str(fp),'sha256':sha(fp),'sourceWorldBox':gb,'sourceCrop':[sx0,sy0,sx1,sy1]},'operation':'restore this patch own geometry pixels in bounded region, apply only shared additive RGB field; no cross-patch artwork copy','maximumRGBDeltaFromOwnGeometry':int(np.abs(a[y0:y1,x0:x1].astype(float)-r[y0:y1,x0:x1]).max()),'resamplingApplied':False,'imageBlur':False,'imagePixelBlend':False,'outsideRegionExactMatch':True}
 out.with_suffix('.png.derivation.json').write_text(json.dumps(rec,indent=2));sel['patches'][key]=out.relative_to(T).as_posix();records.append(key)
(T/'selected-patches.json').write_text(json.dumps(sel,indent=2));print(json.dumps(records))

