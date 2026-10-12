from pathlib import Path
from PIL import Image
import json, hashlib, numpy as np
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def core(tile,r,c):
    sp=ROOT/tile/'records'/f'p{r}{c}.selection.json'
    if not sp.exists(): return None
    s=json.loads(sp.read_text(encoding='utf-8-sig'))
    im=Image.open(s['file']); assert im.size==(1254,1254)
    return im.convert('RGB').crop((115,115,1139,1139)),s
records=[]
groups={'vertical-internal':[],'vertical-left':[],'horizontal':[]}
def seam(name,a,b,axis,group):
    if a is None or b is None: return
    if axis=='vertical':
        im=Image.new('RGB',(256,1024)); im.paste(a[0].crop((896,0,1024,1024)),(0,0)); im.paste(b[0].crop((0,0,128,1024)),(128,0))
        delta=np.abs(np.diff(np.asarray(im).astype(float),axis=1)); edge=delta[:,127,:]; nearby=delta[:,112:144,:]
    else:
        im=Image.new('RGB',(1024,256)); im.paste(a[0].crop((0,896,1024,1024)),(0,0)); im.paste(b[0].crop((0,0,1024,128)),(0,128))
        delta=np.abs(np.diff(np.asarray(im).astype(float),axis=0)); edge=delta[127,:,:]; nearby=delta[112:144,:,:]
    p=OUT/(name+'-native.png'); im.save(p); groups[group].append((name,im))
    records.append({'name':name,'axis':axis,'file':str(p),'dimensions':list(im.size),'sources':[a[1],b[1]],'boundaryMeanAbsChannelDelta':round(float(edge.mean()),3),'nearbyMeanDelta':round(float(nearby.mean()),3)})
for r in range(1,5):
    seam(f'v-p{r}3-p{r}4',core('r04_c11',r,3),core('r04_c11',r,4),'vertical','vertical-internal')
    seam(f'v-p{r}2-p{r}3',core('r04_c11',r,2),core('r04_c11',r,3),'vertical','vertical-left')
for c in [3,4]:
    seam(f'north-c{c}',core('r03_c11',4,c),core('r04_c11',1,c),'horizontal','horizontal')
for r in range(1,4):
    for c in [3,4]:
        seam(f'h-p{r}{c}-p{r+1}{c}',core('r04_c11',r,c),core('r04_c11',r+1,c),'horizontal','horizontal')
for group,items in groups.items():
    for start in range(0,len(items),4):
        subset=items[start:start+4]; sheet=Image.new('RGB',(1024,1024),(128,128,128))
        for i,(_,im) in enumerate(subset): sheet.paste(im,(i*256,0) if group.startswith('vertical') else (0,i*256))
        sheet.save(OUT/f'{group}-sheet-{start//4+1}-native.png')
        (OUT/f'{group}-sheet-{start//4+1}-order.json').write_text(json.dumps([n for n,_ in subset],indent=2)+'\n')
(OUT/'inspection-manifest.json').write_text(json.dumps({'formalAccepted':False,'operation':'native unresampled seam crops only; no candidate assembled','segments':records},indent=2)+'\n')
print(json.dumps([{'name':r['name'],'delta':r['boundaryMeanAbsChannelDelta'],'nearby':r['nearbyMeanDelta']} for r in records]))
