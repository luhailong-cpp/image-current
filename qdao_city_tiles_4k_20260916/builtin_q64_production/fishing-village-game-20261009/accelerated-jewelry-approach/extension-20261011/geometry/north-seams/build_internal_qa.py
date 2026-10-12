from pathlib import Path
from PIL import Image
import json, hashlib, datetime, numpy as np
OUT=Path(__file__).resolve().parent/'new-core-seams'; OUT.mkdir(exist_ok=True)
BASE=OUT.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def get(tile,r,c):
    p=BASE/tile/'records'/f'p{r}{c}.selection.json'
    if not p.exists(): return None
    s=json.loads(p.read_text(encoding='utf-8-sig')); im=Image.open(s['file']).convert('RGB'); assert im.size==(1254,1254)
    return im.crop((115,115,1139,1139)),s
rp=OUT/'partial-qa.json'; prev={}
if rp.exists(): prev={e['segment']:e for e in json.loads(rp.read_text(encoding='utf-8'))['segments']}
records=[]
def seam(name,a,b,axis):
    if a is None or b is None: return
    if axis=='v':
        im=Image.new('RGB',(512,1024)); im.paste(a[0].crop((768,0,1024,1024)),(0,0)); im.paste(b[0].crop((0,0,256,1024)),(256,0)); d=np.abs(np.diff(np.asarray(im).astype(float),axis=1)); edge=d[:,255]
    else:
        im=Image.new('RGB',(1024,512)); im.paste(a[0].crop((0,768,1024,1024)),(0,0)); im.paste(b[0].crop((0,0,1024,256)),(0,256)); d=np.abs(np.diff(np.asarray(im).astype(float),axis=0)); edge=d[255]
    p=OUT/(name+'-native.png'); im.save(p)
    old=prev.get(name,{}); sources=[a[1],b[1]]; same=old.get('sources')==sources
    records.append({'segment':name,'status':old.get('status','awaiting_visual_review') if same else 'awaiting_visual_review','formalAccepted':False,'sources':sources,'file':str(p),'dimensions':list(im.size),'boundaryMeanAbsChannelDelta':round(float(edge.mean()),3),'visualFindings':old.get('visualFindings') if same else None})
for tile in ['r05_c10','r05_c11']:
    for r in range(1,5):
        for c in range(1,4): seam(f'{tile}-v-p{r}{c}-p{r}{c+1}',get(tile,r,c),get(tile,r,c+1),'v')
    for r in range(1,4):
        for c in range(1,5): seam(f'{tile}-h-p{r}{c}-p{r+1}{c}',get(tile,r,c),get(tile,r+1,c),'h')
for r in range(1,5): seam(f'r05-cross-tile-r{r}',get('r05_c10',r,4),get('r05_c11',r,1),'v')
report={'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'scope':'available new core adjacency only; unresampled crops; no candidate changes','availableSegments':len(records),'segments':records}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'segment':r['segment'],'status':r['status'],'delta':r['boundaryMeanAbsChannelDelta']} for r in records]))
