from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent.parent
T=B/'r09_c06';A=T/'pipeline/output/8acb763a3ad68383/assembly.json';d=json.loads(A.read_text(encoding='utf-8-sig'));im=Image.open(d['output']['file']).convert('RGB')
Q=T/'pipeline/qa/full-20261012-8acb763a3ad68383';Q.mkdir(exist_ok=True)
sources={'target':d['output']}; crops=[]
def save(image,name,sourcebox=None):
    p=Q/name;assert not p.exists();image.save(p);crops.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pixels':list(image.size),'QAOnly':True,'sourceBox':sourcebox,'sourceResampling':False});return p
for axis in ['V','H']:
 for s in range(1,4):
    panel=Image.new('RGB',(1024,1048) if axis=='V' else (1024,1120),(245,245,245));draw=ImageDraw.Draw(panel)
    for k in range(4):
        coord=s*1024; start=k*1024
        box=(coord-128,start,coord+128,start+1024) if axis=='V' else (start,coord-128,start+1024,coord+128)
        crop=im.crop(box);save(crop,f'{axis}{s}-{k+1}-native.png',box)
        if axis=='V': panel.paste(crop,(k*256,24));draw.text((k*256+4,5),f'{axis}{s} row{k+1}',fill='black')
        else: panel.paste(crop,(0,k*280+24));draw.text((4,k*280+5),f'{axis}{s} col{k+1}',fill='black')
    save(panel,f'{axis}{s}-native-panel.png')
neigh={'left':B/'r09_c05/pipeline/output/270f210e60b79873/r09_c05.candidate.png','right':B/'r09_c07/repairs-resume-20261012/inner-rim-upper-v01/integrated/r09_c07.candidate.png','bottom':B/'integrated-20261011/v5/r10_c06.candidate.png'}
for side,p in neigh.items():
    n=Image.open(p).convert('RGB');sources[side]={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    panel=Image.new('RGB',(1024,1048) if side!='bottom' else (1024,1120),(245,245,245));draw=ImageDraw.Draw(panel)
    for k in range(4):
        st=k*1024
        if side=='left':c=Image.new('RGB',(256,1024));c.paste(n.crop((3968,st,4096,st+1024)),(0,0));c.paste(im.crop((0,st,128,st+1024)),(128,0))
        elif side=='right':c=Image.new('RGB',(256,1024));c.paste(im.crop((3968,st,4096,st+1024)),(0,0));c.paste(n.crop((0,st,128,st+1024)),(128,0))
        else:c=Image.new('RGB',(1024,256));c.paste(im.crop((st,3968,st+1024,4096)),(0,0));c.paste(n.crop((st,0,st+1024,128)),(0,128))
        save(c,f'{side}-{k+1}-native.png')
        if side!='bottom':panel.paste(c,(k*256,24));draw.text((k*256+4,5),f'{side} row{k+1}',fill='black')
        else:panel.paste(c,(0,k*280+24));draw.text((4,k*280+5),f'bottom col{k+1}',fill='black')
    save(panel,f'{side}-native-panel.png')
whole=Image.new('RGB',(12288,4096));whole.paste(Image.open(neigh['left']),(0,0));whole.paste(im,(4096,0));whole.paste(Image.open(neigh['right']),(8192,0));whole.resize((2304,768)).save(Q/'three-tile-overview-RESIZED-QA-ONLY.png')
(Q/'manifest.json').write_text(json.dumps({'assembly':str(A),'sources':sources,'nativeQACrops':crops,'overviewOnlyResized':True,'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(Q)
