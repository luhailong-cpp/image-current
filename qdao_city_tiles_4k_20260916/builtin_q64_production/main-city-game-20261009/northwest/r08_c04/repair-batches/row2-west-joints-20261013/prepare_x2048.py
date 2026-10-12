from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;T=B.parents[1];D=B/'joint-x2048-01';D.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fs=[T/'native/s02_02_native01.png',T/'native/s02_03_native01.png'];parts=[([512,0,1139,1254],[0,0]),([115,0,742,1254],[627,0])]
im=Image.new('RGB',(1254,1254))
for f,(box,xy) in zip(fs,parts):im.paste(Image.open(f).convert('RGB').crop(box),xy)
im.save(D/'edit-target.png')
for name,box in [('upper-before',[500,200,760,500]),('lower-before',[490,900,770,1170])]:im.crop(box).save(D/(name+'.png'))
(D/'input-provenance.json').write_text(json.dumps({'worldBox':[13709,29581,14963,30835],'tile':'r08_c04','tileBox':[12288,28672,16384,32768],'seamNativeX':627,'formalSourceCoreY':[115,1139],'outerYBands':'context from native halos; no adoption planned','parts':[{'file':str(f),'sha256':sha(f),'sourceBox':box,'targetXY':xy} for f,(box,xy) in zip(fs,parts)],'editTargetSha256':sha(D/'edit-target.png'),'resampled':False},indent=2),encoding='utf-8')

