import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
OUT=Path(__file__).parent
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
j=json.loads((OUT/'source-delta.json').read_text(encoding='utf-8'))
tm={t['tileId']:t for z in j['zones'].values() for t in z['tiles']};d=OUT/'extra-crops';d.mkdir(exist_ok=True);extra=[]
for tile in ['r08_c02','r12_c03']:
 im=Image.open(tm[tile]['file']).convert('RGB');check={'tileId':tile,'source':tm[tile]['file'],'sha256':tm[tile]['sha256'],'boards':[]}
 if tile=='r12_c03':
  for axis in ['vertical','horizontal']:
   for boundary in range(1,4):
    b=Image.new('RGB',(2048,1024));panels=[]
    for s in range(4):
     k=boundary*1024;a=s*1024;box=(k-256,a,k+256,a+1024) if axis=='vertical' else (a,k-256,a+1024,k+256)
     c=im.crop(box);cp=d/f'{tile}-{axis}-{boundary}-segment-{s+1}.png';c.save(cp);b.paste(c,(s*512,0) if axis=='vertical' else ((s%2)*1024,(s//2)*512));panels.append({'path':str(cp),'box':box,'segment':s+1})
    p=d/f'{tile}-{axis}-{boundary}-board.png';b.save(p);check['boards'].append({'path':str(p),'axis':axis,'boundary':boundary,'panels':panels})
  ni=Image.open(tm['r11_c03']['file']).convert('RGB');b=Image.new('RGB',(2048,1024));pans=[]
  for s in range(4):
   a=s*1024;c=Image.new('RGB',(1024,512));c.paste(ni.crop((a,3840,a+1024,4096)),(0,0));c.paste(im.crop((a,0,a+1024,256)),(0,256));b.paste(c,((s%2)*1024,(s//2)*512));cp=d/f'{tile}-north-segment-{s+1}.png';c.save(cp);pans.append(str(cp))
  p=d/f'{tile}-north-board.png';b.save(p);check['northBoard']={'path':str(p),'panels':pans,'neighborSource':tm['r11_c03']['file'],'neighborSha256':tm['r11_c03']['sha256']}
 b=Image.new('RGB',(1536,1536));boxes=[]
 for r in range(1,4):
  for c in range(1,4):
   box=(c*1024-256,r*1024-256,c*1024+256,r*1024+256);b.paste(im.crop(box),((c-1)*512,(r-1)*512));boxes.append(box)
 p=d/f'{tile}-nine-crossings.png';b.save(p);check['crossings']={'path':str(p),'boxes':boxes};extra.append(check)
save(OUT/'extra-checks.json',extra)
# Explicit native-pixel replay for new diagnostic full r08_c02.
t=tm['r08_c02'];im=Image.open(t['file']).convert('RGB');n=0
for s in t['selectedSources']:
 x=(s['subcolumn']-1)*1024;y=(s['subrow']-1)*1024
 with Image.open(s['path']) as si:n+=bool(ImageChops.difference(im.crop((x,y,x+1024,y+1024)),si.convert('RGB').crop((115,115,1139,1139))).getbbox())
save(OUT/'assembly-pixel-verification.json',{'tileId':'r08_c02','coreCount':16,'mismatchingCoreRecrops':n,'pixelCount':4096*4096,'resizing':False,'feathering':False})
print('extra boards',sum(len(c['boards'])+1+bool(c.get('northBoard')) for c in extra))
