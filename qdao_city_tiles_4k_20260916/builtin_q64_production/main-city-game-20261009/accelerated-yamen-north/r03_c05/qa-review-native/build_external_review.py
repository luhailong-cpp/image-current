from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'external-candidate'
OUT.mkdir(exist_ok=True)
files = {
 'target': ROOT/'r03_c05/candidate/r03_c05-pipeline-minimum-error-ece82fe09771-fbbe92.png',
 'west': ROOT/'r03_c04/candidate/r03_c04-pipeline-fixed-native-contexts-3c904a528453.png',
 'south': ROOT/'r04_c05/candidate/r04_c05-pipeline-minimum-error-94abcdd4569b-241dfc.png',
}
imgs = {key:Image.open(path).convert('RGB') for key,path in files.items()}
assert all(im.size == (4096,4096) for im in imgs.values())
sources = {key: {'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'pixels':list(imgs[key].size)} for key,path in files.items()}
items=[]
for side in ['west','south']:
 batch=Image.new('RGB',(1024,4*348),'#e8e8e8')
 d=ImageDraw.Draw(batch)
 for i in range(4):
  q=i*1024
  if side=='west':
   box1=[3936,q,4096,q+1024]; box2=[0,q,160,q+1024]
   strip=Image.new('RGB',(320,1024)); strip.paste(imgs['west'].crop(box1),(0,0)); strip.paste(imgs['target'].crop(box2),(160,0))
   strip=strip.transpose(Image.Transpose.ROTATE_90)
   wb=[16224,8192+q,16544,9216+q]
   src=['west','target']; orientation='90 degrees counterclockwise; target is upper 160 pixels, west is lower 160 pixels'
  else:
   box1=[q,3936,q+1024,4096]; box2=[q,0,q+1024,160]
   strip=Image.new('RGB',(1024,320)); strip.paste(imgs['target'].crop(box1),(0,0)); strip.paste(imgs['south'].crop(box2),(0,160))
   wb=[16384+q,12128,17408+q,12448]
   src=['target','south']; orientation='north target upper 160 pixels; south lower 160 pixels'
  name=f'{side}-segment{i+1:02d}'
  path=OUT/(name+'.png'); strip.save(path)
  d.text((8,i*348+7),name+' | 1:1 native pixels | formal boundary y=160',fill='black')
  batch.paste(strip,(0,i*348+28))
  items.append({'id':name,'file':str(path),'worldBox':wb,'sourceKeys':src,'sourcePixelBoxes':[box1,box2],'orientation':orientation,'displayPixels':[1024,320],'scale':1,'interpolation':'none','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 batch.save(OUT/(side+'-batch-native.png'))
(OUT/'manifest.json').write_text(json.dumps({'sources':sources,'items':items,'purpose':'Formal candidate-to-candidate boundary QA only; pixel crops and rotation, no resize or content edits.'},indent=2),encoding='utf-8')
imgs['target'].crop((864,1250,1184,1750)).save(OUT/'x1024-segment02-detail.png')
print(json.dumps({'output':str(OUT),'sources':sources},indent=2))
