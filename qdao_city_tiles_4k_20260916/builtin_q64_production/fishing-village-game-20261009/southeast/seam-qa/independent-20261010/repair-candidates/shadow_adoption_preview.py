import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
specs=[('S1-hull-shadow',[[730,255],[1050,365],[1000,410],[970,465],[947,630],[910,870],[887,1030],[597,970],[623,845],[655,680],[685,515],[713,350]],(550,200,1080,1120),(30050,41400)),('S2-stone-shadow',[[930,620],[1020,620],[1020,860],[930,860]],(850,540,1080,920),(31700,42350))]
for stem,polygon,crop,origin in specs:
 folder=HERE/(stem+'-adoption-preview');folder.mkdir(exist_ok=True)
 input=HERE/(stem+'-input-100pct.png');repair=HERE/(stem+'-v1.png')
 original=Image.open(input).convert('RGB');result=Image.open(repair).convert('RGB')
 assert original.size==result.size==(1254,1254)
 mask=Image.new('1',original.size);ImageDraw.Draw(mask).polygon([tuple(p) for p in polygon],fill=1)
 composite=original.copy();composite.paste(result,(0,0),mask)
 composite.save(folder/'candidate-preview.png')
 composite.crop(crop).save(folder/'adoption-perimeter-focus.png')
 mask.convert('L').save(folder/'proposed-mask.png')
 mnx,mny=min(p[0] for p in polygon),min(p[1] for p in polygon)
 mxx,mxy=max(p[0] for p in polygon),max(p[1] for p in polygon)
 strips={'left':(max(0,mnx-80),max(0,mny-80),min(1254,mnx+160),min(1254,mxy+80)),'right':(max(0,mxx-160),max(0,mny-80),min(1254,mxx+80),min(1254,mxy+80)),'top':(max(0,mnx-80),max(0,mny-80),min(1254,mxx+80),min(1254,mny+160)),'bottom':(max(0,mnx-80),max(0,mxy-160),min(1254,mxx+80),min(1254,mxy+80))}
 for edge,box in strips.items():composite.crop(box).save(folder/(edge+'.png'))
 rec={'classification':'QA only; original sources and owner selections unchanged','input':str(input),'inputSha256':sha(input),'repair':str(repair),'repairSha256':sha(repair),'nativeMaskPolygon':polygon,'globalMaskPolygon':[[x+origin[0],y+origin[1]] for x,y in polygon],'maskSha256':sha(folder/'proposed-mask.png'),'operation':'binary exact-pixel adoption preview; no resampling, interpolation, blur or feathering','evidence':[{ 'file':str(folder/(f+'.png')),'sha256':sha(folder/(f+'.png'))} for f in ['candidate-preview','adoption-perimeter-focus','left','right','top','bottom']],'selected':False,'formalAccepted':False}
 (folder/'manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps({'stem':stem,'nativeMaskBounds':[mnx,mny,mxx,mxy],'focus':str(folder/'adoption-perimeter-focus.png')}))
