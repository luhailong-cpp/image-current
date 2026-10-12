from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
B=Path(__file__).resolve().parent.parent
def im(n): return Image.open(B/'native'/(n+'.png')).convert('RGB')
sources=['s03_03','s03_04','s04_03_fix01','s04_04_fix01','s04_03_material01','s04_04_material01']
metrics={}
for c in [3,4]:
    north=im(f's03_{c:02d}')
    old=im(f's04_{c:02d}_fix01')
    new=im(f's04_{c:02d}_material01')
    page=Image.new('RGB',(1254,1010),'white');d=ImageDraw.Draw(page)
    for k,(label,south) in enumerate([('BEFORE',old),('AFTER',new)]):
        y=k*505;d.text((8,y+2),f'{label} / NORTH SEAM s03_{c:02d} -> s04_{c:02d} / native pixels',fill=(0,0,0))
        page.paste(north.crop((0,979,1254,1139)),(0,y+25))
        page.paste(south.crop((0,115,1254,435)),(0,y+185))
    f=B/'layout-only'/f's04_{c:02d}_material01.north-compare.png';page.save(f)
    samples={}
    for label,south in [('before',old),('after',new)]:
        na=np.asarray(north,dtype=float)[1024:1254,650:1200]
        sa=np.asarray(south,dtype=float)[:230,650:1200]
        # Excludes x631 grout for c4 and flowers for c3. Different exact microtexture still gives MAE.
        samples[label]={'overlapMeanRGBDeltaSouthMinusNorth':np.mean(sa-na,axis=(0,1)).round(3).tolist(),'overlapMAE':round(float(np.abs(sa-na).mean()),3),'hardSeamMeanAbsoluteJump':round(float(np.abs(np.asarray(north,dtype=float)[1138,650:1200]-np.asarray(south,dtype=float)[115,650:1200]).mean()),3)}
    metrics[f's04_{c:02d}']=samples
left_old=im('s04_03_fix01');right_old=im('s04_04_fix01')
left_new=im('s04_03_material01');right_new=im('s04_04_material01')
page=Image.new('RGB',(1010,1254),'white');d=ImageDraw.Draw(page)
for k,(label,l,r) in enumerate([('BEFORE',left_old,right_old),('AFTER',left_new,right_new)]):
    x=k*505;d.text((x+4,4),label+' / WEST SEAM / native pixels',fill=(0,0,0))
    page.paste(l.crop((979,0,1139,1254)),(x+25,0))
    page.paste(r.crop((115,0,435,1254)),(x+185,0))
page.save(B/'layout-only'/'s04_04_material01.west-compare.png')
metrics['west']={}
for label,l,r in [('before',left_old,right_old),('after',left_new,right_new)]:
    la=np.asarray(l,dtype=float)[0:800,1024:1254];ra=np.asarray(r,dtype=float)[0:800,:230]
    metrics['west'][label]={'overlapMAE':round(float(np.abs(la-ra).mean()),3),'overlapMeanRGBDeltaEastMinusWest':np.mean(ra-la,axis=(0,1)).round(3).tolist(),'hardSeamMeanAbsoluteJump':round(float(np.abs(np.asarray(l,dtype=float)[0:800,1138]-np.asarray(r,dtype=float)[0:800,115]).mean()),3)}
for f in (B/'layout-only').glob('s04_*_material01.*-compare.png'):
    (f.with_suffix('.png.derivation.json')).write_text(json.dumps({'file':str(f),'role':'native-pixel QA comparison; not game art','operation':'unscaled crop and juxtaposition; before and after are separated by whitespace','derivedFrom':[{'file':str(B/'native'/(n+'.png')),'sha256':hashlib.sha256((B/'native'/(n+'.png')).read_bytes()).hexdigest()} for n in sources]},indent=2),encoding='utf-8')
(B/'receipts'/'s04_03_material01.metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))

