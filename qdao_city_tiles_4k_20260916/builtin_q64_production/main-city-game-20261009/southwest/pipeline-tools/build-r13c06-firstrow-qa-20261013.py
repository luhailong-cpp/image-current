from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=B/'r13_c06/pipeline/output/97b324e1ddc5dff2/assembly.json';a=read(ap);im=Image.open(a['output']['file']).convert('RGB');assert im.size==(4096,1024)
q=ap.parent/'root-row1-native-qa';q.mkdir(exist_ok=False)
panel=Image.new('RGB',(3*280,1048),'white');d=ImageDraw.Draw(panel)
for k,x in enumerate([1024,2048,3072]):panel.paste(im.crop((x-128,0,x+128,1024)),(k*280,24));d.text((k*280+3,3),f'V{k+1}',fill='black')
panel.save(q/'three-internal-native-seams.png')
im.resize((1024,256),Image.Resampling.LANCZOS).save(q/'overview-QA-only.png')
e=read(B/'current-candidates.json')['tiles']['r12_c06']['candidate'];assert sha(e['file'])==e['sha256'];top=Image.open(e['file']).convert('RGB')
pan=Image.new('RGB',(1024,4*280),'white');d=ImageDraw.Draw(pan)
for c in range(4):
 x=c*1024;part=Image.new('RGB',(1024,256));part.paste(top.crop((x,3968,x+1024,4096)),(0,0));part.paste(im.crop((x,0,x+1024,128)),(0,128));pan.paste(part,(0,c*280+24));d.text((3,c*280+3),f'TOP{c+1}',fill='black')
pan.save(q/'top-native-boundary-four-segments.png')
atomic_json(q/'manifest.json',{'assembly':str(ap),'assemblySha256':sha(ap),'output':a['output'],'topNeighbor':e,'QAOnly':True,'nativePanelsResampled':False,'overviewOnlyResized':True,'formalAccepted':False,'images':[{'file':str(p),'sha256':sha(p)} for p in q.glob('*.png')]})
print(q)
