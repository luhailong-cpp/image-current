from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
root=Path(__file__).resolve().parents[2]
files=sorted((root/'runtime'/'attack').glob('*/*.png'))
checks=[]
for p in files:
 im=Image.open(p)
 record=json.loads(p.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 checks.append({'file':str(p),'size':im.size,'mode':im.mode,'alpha':im.getextrema()[3],'shaMatches':record.get('sha256')==digest})
for direction in ['E','W']:
 fs=sorted((root/'runtime'/'attack'/direction).glob('*.png'))
 canvas=Image.new('RGB',(1024,3*286),'#e3e7eb'); draw=ImageDraw.Draw(canvas)
 for j,p in enumerate(fs):
  im=Image.open(p).resize((256,256)); xy=((j%4)*256,(j//4)*286)
  canvas.paste(im,xy,im);draw.text((xy[0]+10,xy[1]+259),direction+p.stem,fill='#142634')
 canvas.save(root/'provenance'/'attack'/('review-'+direction+'.jpg'))
(root/'provenance'/'attack'/'technical-check.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(files),'allShaMatches':all(c['shaMatches'] for c in checks)}))
