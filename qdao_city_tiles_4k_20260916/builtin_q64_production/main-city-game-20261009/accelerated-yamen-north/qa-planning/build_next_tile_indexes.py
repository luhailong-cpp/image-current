from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parent.parent
C=json.loads((PROJECT/'production-contract.json').read_text(encoding='utf-8-sig'));S=Path(C['layoutReference']);IM=Image.open(S).convert('RGB');W=65536
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def crop(box,size):
 b=[box[0]*IM.width/W,box[1]*IM.height/W,box[2]*IM.width/W,box[3]*IM.height/W]
 return IM.transform(size,Image.Transform.EXTENT,b,Image.Resampling.BICUBIC),b
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for tr,tc in [(4,5),(3,4),(3,5)]:
 tid=f'r{tr:02}_c{tc:02}';D=HERE/tid;D.mkdir(exist_ok=False);tx=(tc-1)*4096;ty=(tr-1)*4096;tb=[tx,ty,tx+4096,ty+4096]
 tile,_=crop(tb,(1600,1600));grid=Image.new('RGB',(1600,1650),'#17212b');grid.paste(tile,(0,50));dr=ImageDraw.Draw(grid);dr.text((12,10),tid+' | LAYOUT ONLY - NOT GAME ART',(255,255,255),font=font)
 contact=Image.new('RGB',(1600,1760),'#17212b');dc=ImageDraw.Draw(contact);entries=[]
 for r in range(1,5):
  for c in range(1,5):
   pid=f's{r:02}_{c:02}';x=tx+(c-1)*1024;y=ty+(r-1)*1024;core=[x,y,x+1024,y+1024];halo=[x-115,y-115,x+1139,y+1139]
   patch,sb=crop(halo,(1254,1254));p=D/(pid+'.layout-only.png');patch.save(p)
   cx=(c-1)*400;cy=(r-1)*400+50;dr.rectangle((cx,cy,cx+399,cy+399),outline='#ff00b4',width=2);dr.rectangle((cx+4,cy+4,cx+112,cy+35),fill='#17212b');dr.text((cx+8,cy+8),pid,(255,255,255),font=small)
   contact.paste(patch.resize((400,400),Image.Resampling.BILINEAR),((c-1)*400,(r-1)*440+40));dc.text(((c-1)*400+8,(r-1)*440+8),pid+' | layout only',(255,255,255),font=small)
   entries.append({'patch':pid,'file':str(p),'sha256':sha(p),'pixels':[1254,1254],'gameArt':False,'coreWorldBox':core,'worldBoxWithHalo':halo,'sourceBoxFloat':sb,'coreCrop':[115,115,1139,1139]})
 grid.save(D/(tid+'-grid-layout-only.png'));contact.save(D/(tid+'-halo-contact-layout-only.png'))
 meta={'tile':tid,'tileWorldBox':tb,'gameArt':False,'source':str(S),'sourceSha256':sha(S),'sourcePixels':list(IM.size),'layoutPixelToWorldPixels':W/IM.width,'operation':'Bicubic enlarged layout crops only for coordinate planning; not generated game artwork','patches':entries}
 (D/'layout-index.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps({'tile':tid,'worldBox':tb,'directory':str(D)}))
