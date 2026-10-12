from pathlib import Path
from PIL import Image, ImageDraw
import json
T=Path(__file__).resolve().parent;R=T/'repairs';D=T/'review'/'repaired-v2'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=Image.open(read(R/'latest-composition.json')['output']).convert('RGB')
for p in R.glob('*.composition.json'):
    s=read(p);x,y,x2,y2=s['placement']; canvas=Image.new('RGB',(1254,720),'#222222');dr=ImageDraw.Draw(canvas)
    boxes=[('top',[x,y-20,x2,y+140],False),('bottom',[x,y2-140,x2,y2+20],False),('left',[x-20,y,x+140,y2],True),('right',[x2-140,y,x2+20,y2],True)]
    for idx,(label,b,rot) in enumerate(boxes):
        c=a.crop(b)
        if rot:c=c.transpose(Image.Transpose.ROTATE_90)
        dr.text((5,idx*180+2),s['id']+' '+label+' 100% pixels; vertical edges rotated 90 degrees',fill='white')
        canvas.paste(c,(0,idx*180+20))
    canvas.save(D/(s['id']+'-perimeters-100pct.png'))
for pos in [1024,2048,3072]:
    for half in [0,1]:
        lo=half*2048;hi=lo+2048
        a.crop((pos-160,lo,pos+160,hi)).save(D/f'vertical-x{pos}-half{half}-100pct.png')
        a.crop((lo,pos-160,hi,pos+160)).save(D/f'horizontal-y{pos}-half{half}-100pct.png')
print('Created 5 perimeter contact sheets and 12 native seam halves.')
