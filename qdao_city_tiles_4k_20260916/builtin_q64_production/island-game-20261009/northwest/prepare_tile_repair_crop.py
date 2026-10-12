"""Make a strictly unresized crop and full derivation evidence for a native edit."""
from pathlib import Path
from PIL import Image
import json,hashlib,argparse
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
for k in ('stem','tile-id','base','base-record','role'):ap.add_argument('--'+k,required=True)
ap.add_argument('--crop-box',type=int,nargs=4,required=True);a=ap.parse_args()
stem=a.stem;box=a.crop_box;base=Path(a.base).resolve();ass=Path(a.base_record).resolve()
assert all(x.is_relative_to(Z) for x in (base,ass))
assert box[2]-box[0]==box[3]-box[1]==1254 and 0<=box[0]<box[2]<=4096 and 0<=box[1]<box[3]<=4096
r,c=[int(s[1:]) for s in a.tile_id.split('_')];ox=(c-1)*4096;oy=(r-1)*4096
crop=Z/'guides'/f'{stem}.native-crop.png';deriv=Z/'guides'/f'{stem}.native-crop.derivation.json'
ip=Z/'guides'/f'{stem}.input.json';rp=Z/'guides'/f'{stem}.references.json'
assert all(not p.exists() for p in (crop,deriv,ip,rp))
im=Image.open(base);assert im.size==(4096,4096);im.crop(box).save(crop)
d=dict(derivedFrom=dict(path=base.as_posix(),sha256=sha(base),assemblyRecord=dict(path=ass.as_posix(),sha256=sha(ass))),cropBox=box,operation='native-coordinate crop',resizing=False,registration=False,feathering=False,colorCorrection=False,output=dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254]))
deriv.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=[dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254],role=a.role,derivedFrom=d['derivedFrom'])]+json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
rec=dict(stem=stem,tileId=a.tile_id,tileCropBox=box,globalBox=[box[0]+ox,box[1]+oy,box[2]+ox,box[3]+oy],nativeSize=[1254,1254],inputs=inputs,editTarget=dict(path=crop.as_posix(),sha256=sha(crop),derivationRecord=dict(path=deriv.as_posix(),sha256=sha(deriv))),operation='exact native-coordinate crop for builtin local repair',layoutPixelsForbiddenInFinal=True,isFinalArt=False)
ip.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rp.write_text(json.dumps(dict(inputs=inputs),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(crop=crop.as_posix(),input=ip.as_posix(),sha256=sha(crop))))
