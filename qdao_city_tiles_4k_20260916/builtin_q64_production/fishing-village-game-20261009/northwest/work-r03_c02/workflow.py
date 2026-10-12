from pathlib import Path
from PIL import Image
import argparse, json, hashlib, importlib.util
import numpy as np

W = Path(__file__).resolve().parent
ROOT = W.parent
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def resolve(p):
    return Path(p) if Path(p).is_absolute() else ROOT/p
def selected():
    found=[]
    for p in [ROOT/'assembly-plan.json', *ROOT.glob('work-*/selected.json')]:
        if p.exists(): found += [resolve(s['file']) for s in read(p).get('sources', [])]
    return list(dict.fromkeys(found))
def box(ident):
    sr,sc=int(ident.split('_')[2][1:]),int(ident.split('_')[3][1:])
    x,y=4096+(sc-1)*1024,8192+(sr-1)*1024
    return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def prepare(ident):
    c,b=box(ident)
    contract=read(ROOT.parent/'production-contract.json')
    lp=Path(contract['layoutReference']); im=Image.open(lp)
    out=W/'guides'/f'{ident}.layout-and-native-overlap.png'
    if out.exists(): raise RuntimeError('Refuse to overwrite reference guide')
    ob=[v*1254/57344 for v in b]
    guide=im.transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC)
    sources=selected()
    if (W/'guide-overlays.json').exists(): sources += [resolve(p) for p in read(W/'guide-overlays.json')['files']]
    used=[]
    for p in sources:
        if not p.exists(): continue
        r=read(str(p)+'.generation.json'); nb=r['globalNativeBox']
        if r['globalCoreBox'][:2]==c[:2]: continue
        it=[max(b[0],nb[0]),max(b[1],nb[1]),min(b[2],nb[2]),min(b[3],nb[3])]
        if it[2]<=it[0] or it[3]<=it[1]:continue
        src=[it[0]-nb[0],it[1]-nb[1],it[2]-nb[0],it[3]-nb[1]]
        dst=[it[0]-b[0],it[1]-b[1],it[2]-b[0],it[3]-b[1]]
        guide.paste(Image.open(p).crop(src),tuple(dst[:2]))
        used.append({'file':str(p),'sha256':sha(p),'sourceCrop':src,'destinationBox':dst,'globalIntersection':it})
    guide.save(out)
    write(str(out)+'.derivation.json',{'file':str(out),'sha256':sha(out),'role':'layout guide only; scaled layout plus exact unscaled native neighbor context, never final pixels','globalCoreBox':c,'globalNativeBox':b,'nativeCoreCropBox':[115,115,1139,1139],'layout':{'file':str(lp),'sha256':sha(lp)},'overviewFractionalBox':ob,'neighbors':used})
    print(json.dumps({'guide':str(out),'core':c,'native':b,'neighbors':[x['file'] for x in used]}))
def qa(ident):
    p=ROOT/'native'/f'{ident}.png';c,b=box(ident);a=np.array(Image.open(p).convert('RGB'))
    spec=importlib.util.spec_from_file_location('native_assembly',ROOT/'assemble_r03_c03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    entries=[]
    for npth in selected():
        r=read(str(npth)+'.generation.json');nc=r['globalCoreBox'];dx,dy=nc[0]-c[0],nc[1]-c[1]
        if (dx,dy) not in [(-1024,0),(1024,0),(0,-1024),(0,1024)]:continue
        side={(-1024,0):'west',(1024,0):'east',(0,-1024):'north',(0,1024):'south'}[dx,dy]
        n=np.array(Image.open(npth).convert('RGB'));ai=np.ones((1254,1254),np.uint8);ni=np.full((1254,1254),2,np.uint8)
        first,second,fi,si=(n,a,ni,ai) if side in ['west','north'] else (a,n,ai,ni)
        if dy:first,second,fi,si=first.transpose(1,0,2),second.transpose(1,0,2),fi.T,si.T
        joined,ids,d=m.append_hard(first,fi,second,si,side)
        if dy:joined,ids=joined.transpose(1,0,2),ids.T
        prefix=W/'qa'/f'{ident}.{side}'
        Image.fromarray(joined).save(str(prefix)+'.hardcut.png');Image.fromarray(ids).save(str(prefix)+'.source-id.png')
        crop=[0,824,1254,1454] if dy else [824,0,1454,1254]
        Image.fromarray(joined).crop(crop).save(str(prefix)+'.seam100pct.png')
        d.update({'neighbor':str(npth),'neighborSha256':sha(npth),'image':str(prefix)+'.hardcut.png','sourceIdMap':str(prefix)+'.source-id.png','native100PercentCrop':str(prefix)+'.seam100pct.png','cropBox':crop})
        entries.append(d)
    write(W/'qa'/f'{ident}.seams.json',{'candidate':str(p),'sha256':sha(p),'globalNativeBox':b,'methodSource':str(ROOT/'assemble_r03_c03.py'),'methodSourceSha256':sha(ROOT/'assemble_r03_c03.py'),'sourceIds':{'1':str(p),'2':'neighbor defined per seam'},'nativeScale':True,'paths':entries,'visualQA':'pending'})
    print(json.dumps({'patch':ident,'seams':[{'side':e['label'],'image':e['native100PercentCrop'],'MAE':e['overlapMeanAbsoluteRGB']} for e in entries]}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action');ap.add_argument('ident');args=ap.parse_args()
    {'prepare':prepare,'qa':qa}[args.action](args.ident)
