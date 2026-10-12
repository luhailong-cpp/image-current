import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for stem,box,focus,origin in [('S1-hull-shadow',(555,205,1085,1100),(475,125,1165,1180),(30050,41400)),('S2-stone-shadow',(820,390,1070,1010),(740,310,1150,1090),(31700,42350))]:
 folder=HERE/(stem+'-rect-preview');folder.mkdir(exist_ok=True)
 original=Image.open(HERE/(stem+'-input-100pct.png')).convert('RGB');repair=Image.open(HERE/(stem+'-v1.png')).convert('RGB')
 im=original.copy();im.paste(repair.crop(box),box[:2]);im.save(folder/'candidate-preview.png');im.crop(focus).save(folder/'perimeter-focus.png')
 x0,y0,x1,y1=box
 for name,b in [('left',(x0-70,y0-70,x0+70,y1+70)),('right',(x1-70,y0-70,x1+70,y1+70)),('top',(x0-70,y0-70,x1+70,y0+70)),('bottom',(x0-70,y1-70,x1+70,y1+70))]:
  im.crop(b).save(folder/(name+'.png'))
 rec={'classification':'QA only; owner sources unchanged','repair':str(HERE/(stem+'-v1.png')),'repairSha256':sha(HERE/(stem+'-v1.png')),'input':str(HERE/(stem+'-input-100pct.png')),'inputSha256':sha(HERE/(stem+'-input-100pct.png')),'nativeAdoptionBox':box,'globalAdoptionBox':[x0+origin[0],y0+origin[1],x1+origin[0],y1+origin[1]],'operation':'integer native copy/paste only; no scaling, feathering, blending or recoloring','selected':False,'formalAccepted':False,'evidence':[{ 'file':str(folder/(f+'.png')),'sha256':sha(folder/(f+'.png'))} for f in ['candidate-preview','perimeter-focus','left','right','top','bottom']]}
 (folder/'manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
