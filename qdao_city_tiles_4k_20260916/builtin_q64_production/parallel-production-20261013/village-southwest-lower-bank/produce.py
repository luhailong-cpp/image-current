import json, hashlib, sys, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path(__file__).parent
BASE=ROOT.parent.parent
MAP=BASE/'fishing-village-game-20261009'
CON=json.loads((MAP/'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def prep(tile,pr,pc,version='v1'):
    assert tile in ['r12_c03','r12_c04']
    assert not (ROOT/'CONFLICT.json').exists()
    for d in ['guides','native','requests']: (ROOT/d).mkdir(exist_ok=True)
    r,c=int(tile[1:3]),int(tile[5:7]); x=(c-1)*4096+(pc-1)*1024;y=(r-1)*4096+(pr-1)*1024
    box=[x-115,y-115,x+1139,y+1139]; stem=f'{tile}_p{pr:02d}_{pc:02d}_{version}'
    im=Image.open(CON['layoutReference']).convert('RGB'); sc=im.width/57344
    g=im.transform((1254,1254),Image.Transform.EXTENT,tuple(v*sc for v in box),resample=Image.Resampling.NEAREST)
    layout=ROOT/'guides'/f'{stem}-layout-only.png';g.save(layout)
    boundaries=[]
    if pr==1 and c==3:
        a=json.loads((MAP/'southwest/qa/full-tile-r11_c03-assembly.json').read_text())
        for s in a['sources']:
            if s['patch'].startswith('p04_'): boundaries.append((s['path'],s['globalContextBox']))
    for p in (ROOT/'native').glob('*.generation.json'):
        rec=json.loads(p.read_text());
        if rec.get('selected'): boundaries.append((rec['file'],rec['globalContextBox']))
    used=[]
    for path,b in boundaries:
        l,t,rr,bb=max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])
        if rr>l and bb>t and (rr-l<=230 or bb-t<=230):
            src=Image.open(path); g.paste(src.crop((l-b[0],t-b[1],rr-b[0],bb-b[1])),(l-box[0],t-box[1]));used.append({'path':path,'sha256':sha(path),'globalContextBox':b,'intersection':[l,t,rr,bb]})
    guide=ROOT/'guides'/f'{stem}-boundary-guide.png';g.save(guide)
    refs=[guide.as_posix(),CON['detailStyleReference'],str(Path('D:/work/image/designs/mail-ui-v1/01-mail-event.png'))]
    prompt='''Use case: stylized-concept. Create one native 1254 by 1254 square game-map closeup with 1024px central core and 115px halo on all sides. Image 1 is an exact coordinate layout guide: preserve the composition, object scale, silhouettes, positions and perspective, and redraw its blocky low-resolution interior into exquisitely detailed crisp Daoist Q painterly game art. Any already-sharp boundary strip in image 1 is existing native neighbor artwork: keep its geometry, color and texture unchanged and seamlessly continue it into the rest of the image. Do not blur, enlarge existing pixels as a substitute for new detail, or add objects. Image 2 is material and brushwork style only, do NOT copy temple/architecture into this coordinate. Image 3 is the approved fine handpainted Daoist style only, do NOT copy UI, characters, lettering or night lighting. This coordinate is the existing village south-west sandy bank, with existing forms only as visible in image 1. Warm daylight, soft rounded forms, painterly fine detail, natural sandy ground and muted blue-grey rocks where present. No NPC, text, border, grid or labels. Exact square framing; no camera movement, no full scene redesign. Output only the art.'''
    request={'stem':stem,'tile':tile,'patch':f'p{pr:02d}_{pc:02d}','globalContextBox':box,'globalCoreBox':[x,y,x+1024,y+1024],'coreCrop':[115,115,1139,1139],'prompt':prompt,'references':[{'path':p,'sha256':sha(p)} for p in refs],'neighborSources':used,'guideRole':'mechanical layout crop and native boundary paste; not final artwork','tool':'image_gen__imagegen','actualModel':None}
    write(ROOT/'requests'/f'{stem}.json',request)
    records=[json.loads(p.read_text()) for p in (ROOT/'native').glob('*.generation.json')]
    selected={(r['tile'],r['patch']) for r in records if r.get('selected')}
    write(ROOT/'progress.json',{'status':'request_prepared','current':stem,'selectedCores':len(selected),'uniqueSelectedCores':len(selected),'generatedVersions':len(records),'targetCores':32,'complete4kCount':0,'internalPassed4kCount':0})
    print(json.dumps(request))
if __name__=='__main__': prep(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4] if len(sys.argv)>4 else 'v1')
