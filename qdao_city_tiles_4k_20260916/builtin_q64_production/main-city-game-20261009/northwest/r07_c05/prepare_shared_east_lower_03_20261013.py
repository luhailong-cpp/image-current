from pathlib import Path
from datetime import datetime,timezone
import sys
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
D=T/'bridges/shared-east-lower-03';D.mkdir(exist_ok=False)
base=T/'bridges/shared-east-lower-02/trial-native-roi.png';im=Image.open(base).convert('RGB');d=ImageDraw.Draw(im)
segments=[(215,223),(727,756),(813,889)]
for a,b in segments:
 d.line([(627,a),(627,b)],fill=(0,210,255),width=3)
 for y in (a,b):d.ellipse((617,y-10,637,y+10),outline=(240,0,180),width=2)
guide=D/'layout-locator-only.png';im.save(guide)
prompt='''Use case: precise-object-edit. Edit image 1 at its exact native 1254x1254 size and framing. Image 2 is an annotation locator only: cyan vertical strokes and magenta endpoint circles locate THREE short missing stone grout connectors.
Change only these three tiny local connectors at x627: y215 to223, y727 to756, and y813 to889. Turn each cyan stroke into the same narrow recessed brown grout with the same ivory bevel as the adjacent existing joints. The original diagonal tips must stay exactly where they are, connected by the indicated vertical jog. Keep the deliberately staggered stone geometry; do not regularize the grid, move any gold vertex or shift a diagonal. The previously repaired vertical connector at x627 y502..552 is correct and must remain unchanged.
Preserve all original hand-painted ivory stone texture, tiny lattice ornament, gold node highlights, palette, scale and exact large diamond outlines. Outside x610..645 within the three marked vertical ranges plus 8 pixels, keep the original image unchanged. No global redraw, no texture smoothing, no extra object, no changed camera, no resizing or crop. Remove all cyan and magenta locator ink. Return opaque native 1254x1254 PNG, with only the three original discontinuities closed.'''
args={'prompt':prompt,'referenced_image_paths':[str(base),str(guide)],'transparent_background':False}
(D/'prompt.txt').write_text(prompt,encoding='utf-8');p.write_json(D/'parameters.json',args,replace=False)
ref=lambda f:{'file':str(f),'sha256':p.sha(f)}
p.write_json(D/'request.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','parameters':args,'actualModel':None,'actualQuality':None,'paidAPIUsed':False,'references':[dict(ref(base),role='exact edit target'),dict(ref(guide),role='locator only not production art')],'worldBox':[19853,26776,21107,28030],'tileOrigins':{'r07_c05':[3469,2200],'r07_c06':[-627,2200]},'nativePixels':[1254,1254],'sourceResampled':False,'targetVerticalSegments':segments},replace=False)
print(D)
