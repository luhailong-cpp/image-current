"""Insert reviewed native curb contribution into both adjacent tiles, without resampling."""
import hashlib
import json
from pathlib import Path
from PIL import Image

Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):
    p=Path(p);assert not p.exists(),str(p)
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(p):
    p=Path(p);return p if p.is_absolute() else Z/p
def parent(p):
    r=Path(str(p)+'.derived.json');kind='derivedRecord'
    if not r.exists():r=Path(str(p)+'.generation.json');kind='generationRecord'
    return {'path':str(p),'sha256':sha(p),kind:{'path':str(r),'sha256':sha(r)}}

rp=Z/'native/r07_c12_v4-curb42-43-bridge-v3.png'
assert sha(rp)=='746b786ed307ac489db4fcd6e99a3b65f7588feeb193db9879e806ec8ed688e8'
world=[46529,23743,47783,24997]
active=[46529,23973,47668,24882]
repair=Image.open(rp).convert('RGB');assert repair.size==(1254,1254)
for tile,old in [('r06_c12','r06_c12.selection-v4.json'),('r07_c12','r07_c12.selection-west-v4.json')]:
    source=Z/'records'/old;selection=read(source);chosen={}
    origin=[(int(tile[5:])-1)*4096,(int(tile[1:3])-1)*4096]
    for pid,item in selection['patches'].items():
        p=resolve(item if isinstance(item,str) else item['path'])
        if isinstance(item,dict):assert sha(p)==item['sha256']
        row,col=int(pid[-2]),int(pid[-1])
        cx,cy=origin[0]+(col-1)*1024,origin[1]+(row-1)*1024
        box=[cx-115,cy-115,cx+1139,cy+1139]
        intersection=[max(box[0],active[0]),max(box[1],active[1]),min(box[2],active[2]),min(box[3],active[3])]
        if intersection[0]<intersection[2] and intersection[1]<intersection[3]:
            coordinate={'id':pid,'coreGlobalBox':[cx,cy,cx+1024,cy+1024],'nativeGlobalBox':box,'nativeCoreBox':[115,115,1139,1139],'expectedSize':[1254,1254]}
            crop=[intersection[0]-world[0],intersection[1]-world[1],intersection[2]-world[0],intersection[3]-world[1]]
            xy=[intersection[0]-box[0],intersection[1]-box[1]]
            im=Image.open(p).convert('RGB');piece=repair.crop(crop);im.paste(piece,xy)
            assert im.crop([xy[0],xy[1],xy[0]+piece.width,xy[1]+piece.height]).tobytes()==piece.tobytes()
            out=Z/'native'/f'{pid}-closure-v5.png';assert not out.exists();im.save(out)
            save(str(out)+'.derived.json',{'schemaVersion':1,'file':str(out),'sha256':sha(out),'coordinates':coordinate,'nativeGlobalBox':box,'pixels':[1254,1254],'operation':'Exact integer crop and opaque paste; no resize, transform, paint or blending','derivedFrom':[parent(p),parent(rp)],'contributions':[{'source':str(rp),'sourceCropBox':crop,'pasteAt':xy,'worldBox':intersection}],'formalAccepted':False})
            p=out
        chosen[pid]={'path':str(p),'sha256':sha(p)}
    out=Z/'records'/f'{tile}.selection-closure-v5.json'
    save(out,{'tile':tile,'patches':chosen,'status':'candidate_native_insertion_QA_pending','sourceSelection':{'path':str(source),'sha256':sha(source)},'replacesHistoricalSources':False})
    print(out)
