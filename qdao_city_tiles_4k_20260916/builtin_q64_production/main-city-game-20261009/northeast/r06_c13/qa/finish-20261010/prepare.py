"""Build complete tile base including prior two north-edge repairs, then repair inputs."""
from pathlib import Path
from PIL import Image
import json,hashlib
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1];ZONE=TILE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for sub in ['inputs','source','prompts','receipts','records','review']:(HERE/sub).mkdir(exist_ok=True)
baseline=TILE/'qa/core-baseline/6c2e5c13cfbe255b4af6/r06_c13-core-baseline.candidate.png'
south_repairs=ZONE/'qa/south-join-20261010/repairs'
base=Image.open(baseline).convert('RGB')
ops=[]
for repair in read(south_repairs/'repair-review.json')['repairs']:
    rawpath=south_repairs/repair['source'];raw=Image.open(rawpath).convert('RGB')
    for op in repair['integerTileOperations']:
        if op['tile']!='r06_c13':continue
        maskpath=south_repairs/repair['binaryMask'] if 'binaryMask' in repair else None
        mask=Image.open(maskpath).crop(op['maskCrop']) if maskpath else None
        base.paste(raw.crop(op['sourceCrop']),tuple(op['destinationTileXY']),mask)
        ops.append({'source':str(rawpath),'sha256':sha(rawpath),'sourceCrop':op['sourceCrop'],'destinationTileXY':op['destinationTileXY'],'mask':str(maskpath) if maskpath else None,'maskSha256':sha(maskpath) if maskpath else None,'maskCrop':op.get('maskCrop')})
basepath=HERE/'inputs/base-with-north-repairs.png';assert not basepath.exists();base.save(basepath)
save(HERE/'records/base-replay.json',{'baseline':str(baseline),'baselineSha256':sha(baseline),'operations':ops,'output':str(basepath),'outputSha256':sha(basepath),'noResize':True,'formalAcceptedCount':0})
northpath=ZONE/'r05_c13/candidates/r05_c13.candidate.png';north=Image.open(northpath).convert('RGB')
assert sha(northpath)=='5322cfcd3254b15441e66ecc1fd1103cb96d10c9efc659e7b9afdc555e8b6dc4'
cases=[{'id':'roof-cross-seam-v1','origin':[51600,20280],'editContextBox':[460,120,790,1220],'sources':[(north,northpath,[49152,16384]),(base,basepath,[49152,20480])]},
       {'id':'p23-flower-corner-v1','origin':[50572,20930],'editContextBox':[430,390,900,880],'sources':[(base,basepath,[49152,20480])]}]
for case in cases:
    x,y=case['origin'];out=Image.new('RGB',(1254,1254));coverage=Image.new('L',(1254,1254));sources=[]
    for image,path,(ox,oy) in case['sources']:
        w=[max(x,ox),max(y,oy),min(x+1254,ox+4096),min(y+1254,oy+4096)]
        if w[0]>=w[2] or w[1]>=w[3]:continue
        crop=[w[0]-ox,w[1]-oy,w[2]-ox,w[3]-oy];dest=[w[0]-x,w[1]-y]
        out.paste(image.crop(crop),tuple(dest));coverage.paste(255,(dest[0],dest[1],dest[0]+w[2]-w[0],dest[1]+w[3]-w[1]))
        sources.append({'file':str(path),'sha256':sha(path),'crop':crop,'paste':dest})
    assert coverage.getextrema()==(255,255)
    path=HERE/'inputs'/f"{case['id']}.png";out.save(path)
    save(HERE/'records'/f"{case['id']}.input.json",{'id':case['id'],'context':str(path),'sha256':sha(path),'contextWorldBox':[x,y,x+1254,y+1254],'editContextBox':case['editContextBox'],'composition':sources,'operation':'integer crop/paste native or candidate pixels; no resize'})
    print(str(path))
