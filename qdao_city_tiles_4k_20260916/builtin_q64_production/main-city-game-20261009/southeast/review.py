from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
B=Path(__file__).resolve().parent;T=B/'r13_c13'
mapping=json.loads((T/'active-native-map.json').read_text(encoding='utf-8'))
imgs={k:Image.open(T/'native'/f'{v}.png').convert('RGB') for k,v in mapping.items()}
out=[]
for key,a in imgs.items():
    r=int(key[1:3]);c=int(key[4:6])
    for axis,nbr in [('H',f'p{r:02d}_{c+1:02d}'),('V',f'p{r+1:02d}_{c:02d}')]:
        if nbr not in imgs:continue
        if axis=='H':aa=a.crop((1024,0,1254,1254));bb=imgs[nbr].crop((0,0,230,1254))
        else:aa=a.crop((0,1024,1254,1254)).transpose(Image.Transpose.ROTATE_90);bb=imgs[nbr].crop((0,0,1254,230)).transpose(Image.Transpose.ROTATE_90)
        diff=np.abs(np.asarray(aa,dtype=np.int16)-np.asarray(bb,dtype=np.int16))
        board=Image.new('RGB',(460,1254));board.paste(aa,(0,0));board.paste(bb,(230,0))
        p=T/'review'/f'{key}-{nbr}-{axis}-overlap100pct.png';board.save(p)
        out.append({'a':key,'b':nbr,'axis':axis,'overlap':230,'meanAbsoluteDifference':float(diff.mean()),'p95':float(np.percentile(diff,95)),'identicalPixelsFraction':float((diff.max(axis=2)==0).mean()),'reviewImage':str(p),'status':'requires_visual_review'})
preview=Image.new('RGB',(4096,4096),(38,44,49));d=ImageDraw.Draw(preview)
for r in range(4):
    for c in range(4):
        k=f'p{r+1:02d}_{c+1:02d}'
        if k in imgs:preview.paste(imgs[k].crop((115,115,1139,1139)),(c*1024,r*1024))
        else:d.line((c*1024,r*1024,(c+1)*1024,(r+1)*1024),fill=(70,76,82),width=8)
preview.resize((1024,1024),Image.Resampling.LANCZOS).save(T/'review'/'partial-coverage-preview-only.png')
(T/'review'/'overlap-metrics.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
p=B/'progress.json';data=json.loads(p.read_text(encoding='utf-8-sig'));data['activeNativePatchCount']=len(imgs);data['activeNativeMap']=str(T/'active-native-map.json');data['generatedNativeCount']=len(list((T/'native').glob('*.generation.json')));p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out))
