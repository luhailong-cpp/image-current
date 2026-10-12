from pathlib import Path
from PIL import Image
import json, hashlib, numpy as np
OUT=Path(__file__).resolve().parent/'all-seams'
OUT.mkdir(exist_ok=True)
ROOT=OUT.parents[3]
def core(tile,r,c):
    p=ROOT/tile/'records'/f'p{r}{c}.selection.json'
    s=json.loads(p.read_text(encoding='utf-8-sig'))
    im=Image.open(s['file']); assert im.size==(1254,1254)
    return im.convert('RGB').crop((115,115,1139,1139)),s
records=[]
groups={}
def seam(name,a,b,axis,group):
    if axis=='v':
        im=Image.new('RGB',(256,1024)); im.paste(a[0].crop((896,0,1024,1024)),(0,0)); im.paste(b[0].crop((0,0,128,1024)),(128,0))
        wide=Image.new('RGB',(512,1024)); wide.paste(a[0].crop((768,0,1024,1024)),(0,0)); wide.paste(b[0].crop((0,0,256,1024)),(256,0))
        d=np.abs(np.diff(np.asarray(im).astype(float),axis=1)); edge=d[:,127,:]; nearby=d[:,112:144,:]
    else:
        im=Image.new('RGB',(1024,256)); im.paste(a[0].crop((0,896,1024,1024)),(0,0)); im.paste(b[0].crop((0,0,1024,128)),(0,128))
        wide=Image.new('RGB',(1024,512)); wide.paste(a[0].crop((0,768,1024,1024)),(0,0)); wide.paste(b[0].crop((0,0,1024,256)),(0,256))
        d=np.abs(np.diff(np.asarray(im).astype(float),axis=0)); edge=d[127,:,:]; nearby=d[112:144,:,:]
    p=OUT/(name+'.png'); im.save(p); wide.save(OUT/(name+'-wide.png')); groups.setdefault(group,[]).append((name,im))
    records.append({'name':name,'axis':axis,'file':str(p),'sources':[a[1],b[1]],'boundaryMeanAbsChannelDelta':round(float(edge.mean()),3),'nearbyMeanDelta':round(float(nearby.mean()),3)})
for c in range(1,4):
    for r in range(1,5): seam(f'v-p{r}{c}-p{r}{c+1}',core('r04_c11',r,c),core('r04_c11',r,c+1),'v',f'v-c{c}')
for r in range(1,4):
    for c in range(1,5): seam(f'h-p{r}{c}-p{r+1}{c}',core('r04_c11',r,c),core('r04_c11',r+1,c),'h',f'h-r{r}')
for c in range(1,5): seam(f'north-c{c}',core('r03_c11',4,c),core('r04_c11',1,c),'h','north')
for r in range(1,5): seam(f'west-r{r}',core('r04_c10',r,4),core('r04_c11',r,1),'v','west')
for group,items in groups.items():
    sheet=Image.new('RGB',(1024,1024),(128,128,128))
    for i,(name,im) in enumerate(items): sheet.paste(im,(i*256,0) if im.width==256 else (0,i*256))
    sheet.save(OUT/(group+'-sheet-native.png'))
    (OUT/(group+'-order.json')).write_text(json.dumps([n for n,_ in items],indent=2)+'\n')
(OUT/'inspection-manifest.json').write_text(json.dumps({'formalAccepted':False,'operation':'native unresampled seam crops only; no candidate assembled','segments':records},indent=2)+'\n')
print(json.dumps([{'name':r['name'],'delta':r['boundaryMeanAbsChannelDelta'],'nearby':r['nearbyMeanDelta']} for r in records]))
