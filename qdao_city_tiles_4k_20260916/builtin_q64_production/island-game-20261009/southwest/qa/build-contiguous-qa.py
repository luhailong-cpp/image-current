"""Native hard-paste review views for the active four-tile group; QA only."""
from pathlib import Path
import sys,argparse,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import ROOT,load,dump,hashfile,now,metadata
from PIL import Image

ap=argparse.ArgumentParser()
ap.add_argument('--spec',required=True)
ap.add_argument('--prefix',required=True)
a=ap.parse_args()
assert re.fullmatch(r'[A-Za-z0-9_-]+',a.prefix)
spec=load(a.spec); qa=ROOT/'qa'; images={}; sources=[]
for tile in ['r09_c03','r09_c04','r10_c03','r10_c04']:
    pre=spec[tile]
    p=qa/f'{pre}-candidate-4096.png'; report=load(qa/f'{pre}-report.json')
    im=Image.open(p).convert('RGB'); assert im.size==(4096,4096)
    assert report['tile']==tile
    images[tile]=im
    sources.append({**metadata(p,'native4096 candidate'),'report':str(qa/f'{pre}-report.json'),'mask':str(qa/f'{pre}-source-id-mask.png')})
canvas=Image.new('RGB',(8192,8192))
for tile,x,y in [('r09_c03',0,0),('r09_c04',4096,0),('r10_c03',0,4096),('r10_c04',4096,4096)]: canvas.paste(images[tile],(x,y))
outputs=[]
def save(im,suffix,box=None,op='same-coordinate native hard crop/paste, no resampling'):
    p=qa/f'{a.prefix}-{suffix}.png'; assert not p.exists(); im.save(p)
    outputs.append({**metadata(p,op),'compositeCrop':box})
save(canvas.resize((2048,2048),Image.Resampling.LANCZOS),'preview-2048-QA-only',None,'4:1 downsampled display preview only, no final contribution')
for direction in ['vertical','horizontal']:
    for i in range(8):
        box=[3796,i*1024,4396,(i+1)*1024] if direction=='vertical' else [i*1024,3796,(i+1)*1024,4396]
        save(canvas.crop(box),f'{direction}-{i+1}-native100',box)
box=[3469,3469,4723,4723];save(canvas.crop(box),'four-way-junction-native100',box)
dump(qa/f'{a.prefix}-manifest.json',{'createdAtUtc':now(),'globalBox':[8192,32768,16384,40960],'spec':spec,'sources':sources,'outputs':outputs,'status':'awaiting visual QA','formalAccepted':False})
print(str(qa/f'{a.prefix}-manifest.json'))
