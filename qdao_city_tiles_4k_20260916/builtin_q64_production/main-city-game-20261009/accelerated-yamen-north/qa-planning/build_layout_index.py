from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PROJECT=ROOT.parent
C=json.loads((PROJECT/'production-contract.json').read_text(encoding='utf-8-sig'))
S=Path(C['layoutReference'])
IM=Image.open(S).convert('RGB')
CANVAS=65536
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(im,p):
    if p.exists():raise FileExistsError(p)
    im.save(p,format='PNG')
def cropworld(box,size):
    b=[box[0]*IM.width/CANVAS,box[1]*IM.height/CANVAS,box[2]*IM.width/CANVAS,box[3]*IM.height/CANVAS]
    return IM.transform(size,Image.Transform.EXTENT,b,Image.Resampling.BICUBIC),b

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
tilebox=[12288,12288,16384,16384]
tile,_=cropworld(tilebox,(1600,1600))
grid=Image.new('RGB',(1600,1650),'#17212b');grid.paste(tile,(0,50));dr=ImageDraw.Draw(grid)
dr.text((12,10),'r04_c04 | LAYOUT ONLY - NOT GAME ART',(255,255,255),font=font)
contact=Image.new('RGB',(1600,1760),'#17212b');dc=ImageDraw.Draw(contact)
entries=[]
for r in range(1,5):
 for col in range(1,5):
    pid=f's{r:02d}_{col:02d}'
    x,y=12288+(col-1)*1024,12288+(r-1)*1024
    box=[x-115,y-115,x+1139,y+1139]
    core=[x,y,x+1024,y+1024]
    patch,sourcebox=cropworld(box,(1254,1254))
    p=HERE/(pid+'.layout-only.png');save(patch,p)
    contact.paste(patch.resize((400,400),Image.Resampling.BILINEAR),((col-1)*400,(r-1)*440+40))
    dc.text(((col-1)*400+8,(r-1)*440+8),pid+' | layout-only',(255,255,255),font=small)
    cx,cy=(col-1)*400,(r-1)*400+50
    dr.rectangle((cx,cy,cx+399,cy+399),outline=(255,0,180),width=2)
    dr.rectangle((cx+4,cy+4,cx+112,cy+35),fill='#17212b')
    dr.text((cx+8,cy+8),pid,(255,255,255),font=small)
    entries.append({'patch':pid,'file':str(p),'sha256':sha(p),'pixels':[1254,1254],'gameArt':False,
                    'coreWorldBox':core,'worldBoxWithHalo':box,'sourceBoxFloat':sourcebox,'coreCrop':[115,115,1139,1139]})
save(grid,HERE/'r04_c04-grid-layout-only.png')
save(contact,HERE/'r04_c04-halo-contact-layout-only.png')
meta={'tile':'r04_c04','tileWorldBox':tilebox,'gameArt':False,'source':str(S),'sourceSha256':sha(S),'sourcePixels':list(IM.size),
      'layoutPixelToWorldPixels':CANVAS/IM.width,'operation':'Bicubic enlarged overview crops only for coordinate reference; never generated game artwork',
      'patches':entries}
(HERE/'layout-index.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')

n=ROOT/'r04_c04/native/s04_01_fix02.png'
s=PROJECT/'northwest/r05_c04/native/s01_01.png'
N=Image.open(n).convert('RGB');B=Image.open(s).convert('RGB')
hard=Image.new('RGB',(1254,640));hard.paste(N.crop((0,819,1254,1139)),(0,0));hard.paste(B.crop((0,115,1254,435)),(0,320))
save(hard,HERE/'s04_01_fix02-south-hard-join-native.png')
pair=Image.new('RGB',(1254,500),'#17212b');pair.paste(N.crop((0,1024,1254,1254)),(0,20));pair.paste(B.crop((0,0,1254,230)),(0,270))
d=ImageDraw.Draw(pair);d.text((8,0),'NEW y1024..1253',(255,255,255),font=small);d.text((8,250),'EXISTING SOUTH y0..229',(255,255,255),font=small)
save(pair,HERE/'s04_01_fix02-south-overlap-pair-native.png')
diff=np.abs(np.array(N.crop((0,1024,1254,1254))).astype(np.int16)-np.array(B.crop((0,0,1254,230))).astype(np.int16))
diagnostic={'new':{'file':str(n),'sha256':sha(n)},'south':{'file':str(s),'sha256':sha(s)},'overlapNewBox':[0,1024,1254,1254],
            'overlapSouthBox':[0,0,1254,230],'meanAbsDifference':float(diff.mean()),'p95AbsDifference':float(np.percentile(diff,95)),
            'identicalPixels':int(np.all(diff==0,axis=2).sum()),'overlapPixels':1254*230,'diagnosticOnly':True,'nativePixelScale':1,
            'hardJoin':{'file':str(HERE/'s04_01_fix02-south-hard-join-native.png'),'seamImageY':320,'worldSeamY':16384,
                        'worldBox':[12173,16064,13427,16704]},'formalAccepted':False}
(HERE/'s04_01_fix02-south-diagnostics.json').write_text(json.dumps(diagnostic,indent=2),encoding='utf-8')
print(json.dumps({'index':str(HERE/'layout-index.json'),'grid':str(HERE/'r04_c04-grid-layout-only.png'),'contact':str(HERE/'r04_c04-halo-contact-layout-only.png'),'boundary':diagnostic},indent=2))
