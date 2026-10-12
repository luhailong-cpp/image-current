"""Versioned exact native contributions for the first block west fascia repair."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

Z=Path(__file__).resolve().parent
VERSION=sys.argv[1] if len(sys.argv)>1 else 'v2'
assert VERSION in ('v2','v3','v4')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(p):p=Path(p);return p if p.is_absolute() else Z/p
def parent(p):
    record=Path(str(p)+'.derived.json')
    kind='derivedRecord'
    if not record.exists():record=Path(str(p)+'.generation.json');kind='generationRecord'
    return {'path':str(p),'sha256':sha(p),kind:{'path':str(record),'sha256':sha(record)}}

contributions=[
    ('root-west-reconstruction-v2.png',[48525,25900,49779,27154],[250,115,1139,1139]),
    ('root-west-corner-continuation-v1.png',[49037,26509,50291,27763],[0,0,880,850]),
]
if VERSION in ('v3','v4'):
    contributions.append(('root-west-deck-join-v1.png',[48525,25388,49779,26642],[500,0,1000,1254 if VERSION=='v4' else 850]))
for tile,selection_name in [('r07_c12','r07_c12.selection-v1.json'),('r07_c13','r07_c13.selection-v1.json')]:
    selection=read(Z/'records'/selection_name)
    origin=[(int(tile[5:])-1)*4096,(int(tile[1:3])-1)*4096]
    chosen={}
    for pid,item in selection['patches'].items():
        p=resolve(item if isinstance(item,str) else item['path'])
        if isinstance(item,dict):assert sha(p)==item['sha256']
        row,col=int(pid[-2]),int(pid[-1])
        cx,cy=origin[0]+(col-1)*1024,origin[1]+(row-1)*1024
        box=[cx-115,cy-115,cx+1139,cy+1139]
        coordinate={'id':pid,'coreGlobalBox':[cx,cy,cx+1024,cy+1024],'nativeGlobalBox':box,'nativeCoreBox':[115,115,1139,1139],'expectedSize':[1254,1254]}
        im=Image.open(p).convert('RGB');parents=[parent(p)];operations=[]
        for name,world,crop in contributions:
            rp=Z/'native'/name;active=[world[0]+crop[0],world[1]+crop[1],world[0]+crop[2],world[1]+crop[3]]
            intersection=[max(box[0],active[0]),max(box[1],active[1]),min(box[2],active[2]),min(box[3],active[3])]
            if intersection[0]>=intersection[2] or intersection[1]>=intersection[3]:continue
            source_crop=[intersection[0]-world[0],intersection[1]-world[1],intersection[2]-world[0],intersection[3]-world[1]]
            xy=(intersection[0]-box[0],intersection[1]-box[1])
            piece=Image.open(rp).convert('RGB').crop(source_crop);im.paste(piece,xy)
            assert im.crop((xy[0],xy[1],xy[0]+piece.width,xy[1]+piece.height)).tobytes()==piece.tobytes()
            parents.append(parent(rp));operations.append({'source':str(rp),'sourceCropBox':source_crop,'pasteAt':list(xy),'worldBox':intersection})
        if operations:
            out=Z/'native'/f'{pid}-west-repair-{VERSION}.png';assert not out.exists();im.save(out)
            save(str(out)+'.derived.json',{'schemaVersion':1,'file':str(out),'sha256':sha(out),'coordinates':coordinate,'nativeGlobalBox':box,'pixels':[1254,1254],'operation':'Exact integer crop and opaque paste of builtin generated native sources, in recorded order; no resize, transform, paint or blend','derivedFrom':parents,'contributions':operations,'formalAccepted':False})
            chosen[pid]={'path':str(out),'sha256':sha(out)}
        else:chosen[pid]={'path':str(p),'sha256':sha(p)}
    out=Z/'records'/f'{tile}.selection-west-{VERSION}.json';assert not out.exists()
    save(out,{'tile':tile,'patches':chosen,'status':'candidate_native_insertion_QA_pending','replacesHistoricalSources':False})
    print(str(out))
