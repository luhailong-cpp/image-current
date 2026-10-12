from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;T=B.parents[1]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources=[T/'native/s02_01_native01.png',T/'native/s02_02_native01.png']
im=Image.new('RGB',(1254,1254));parts=[([512,0,1139,1254],[0,0]),([115,0,742,1254],[627,0])]
for f,(box,pos) in zip(sources,parts):im.paste(Image.open(f).convert('RGB').crop(box),pos)
out=B/'joint-x1024-01';out.mkdir(parents=True,exist_ok=False)
im.save(out/'edit-target.png')
locator=im.copy();d=ImageDraw.Draw(locator)
for box in [(607,378,652,438),(607,780,654,858)]:d.rectangle(box,outline=(0,220,230),width=2)
locator.save(out/'locator-only.png')
for name,box in [('upper-before',(530,330,730,485)),('lower-before',(525,730,735,900))]:im.crop(box).save(out/(name+'.png'))
(out/'input-provenance.json').write_text(json.dumps({'worldBox':[12685,29581,13939,30835],'tile':'r08_c04','tileBox':[12288,28672,16384,32768],'seamNativeX':627,'formalSourceCoreY':[115,1139],'outerYBands':'context from native halos; no adoption planned','parts':[{'file':str(f),'sha256':sha(f),'sourceBox':box,'targetXY':pos} for f,(box,pos) in zip(sources,parts)],'editTargetSha256':sha(out/'edit-target.png'),'locatorOnly':True,'resampled':False,'mutations':'exact native crops only; locator annotation never production'},indent=2),encoding='utf-8')
print(out)

