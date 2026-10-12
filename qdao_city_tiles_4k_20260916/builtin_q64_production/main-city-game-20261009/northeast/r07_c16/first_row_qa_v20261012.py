from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(tile,patch):
    selection=json.loads((tile/'selected-native.json').read_text(encoding='utf-8-sig'))
    p=tile/'native'/selection[patch]
    r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
    assert r['sha256']==sha(p) and r['nativeSize']==[1254,1254]
    return p
paths=[source(T,f'p1{c}') for c in range(1,5)]
west=source(T.parent/'r07_c15','p14')
sig=hashlib.sha256(''.join(sha(p) for p in [west]+paths).encode()).hexdigest()[:20]
out=T/'qa'/'first-row-v20261012'/sig
out.mkdir(parents=True,exist_ok=True)
def emit(im,path):
    if path.exists():
        old=Image.open(path);assert old.size==im.size and old.convert('RGB').tobytes()==im.convert('RGB').tobytes()
    else:im.save(path)
    return {'file':str(path),'sha256':sha(path),'size':list(im.size),'resized':False}
ims=[Image.open(p).convert('RGB') for p in paths]
row=Image.new('RGB',(4096,1024))
for c,im in enumerate(ims):row.paste(im.crop((115,115,1139,1139)),(c*1024,0))
artifacts=[dict(emit(row,out/'first-row-native.png'),kind='first-row-native-core-paste')]
for c in range(1,4):
    box=[c*1024-256,0,c*1024+256,1024]
    artifacts.append(dict(emit(row.crop(box),out/f'vertical-p1{c}-p1{c+1}-join-100pct.png'),kind='internal-seam',crop=box,seamX=256))
w=Image.open(west).convert('RGB')
join=Image.new('RGB',(512,1024));join.paste(w.crop((883,115,1139,1139)),(0,0));join.paste(ims[0].crop((115,115,371,1139)),(256,0))
artifacts.append(dict(emit(join,out/'west-r07c15-p14-r07c16-p11-join-100pct.png'),kind='shared-west-seam',seamX=256))
report={'tile':T.name,'inputSignature':sig,'nativeSources':[{'file':str(p),'sha256':sha(p)} for p in [west]+paths],'artifacts':artifacts,'operation':'integer native core crops/pastes only; no resizing, blending or color correction','visualStatus':'unreviewed'}
(out/'export.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(out)
