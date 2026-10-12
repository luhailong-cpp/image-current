from pathlib import Path
from datetime import datetime,timezone
import sys
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
D=T/'bridges/shared-east-lower-04';D.mkdir(exist_ok=False)
base=T/'bridges/shared-east-lower-03/trial-bottom-only.png';im=Image.open(base).convert('RGB');d=ImageDraw.Draw(im)
d.line([(627,727),(627,756)],fill=(0,210,255),width=3)
for y in (727,756):d.ellipse((619,y-8,635,y+8),outline=(240,0,180),width=2)
d.rectangle((570,754,597,780),outline=(0,180,90),width=2)
guide=D/'layout-locator-only.png';im.save(guide)
prompt='''Use case: precise-object-edit. Output the exact same 1254x1254 map crop as image 1. Image 2 is a locator overlay only. Perform ONE tiny surgical repair at x627 y727..756. Replace the cyan 29-pixel VERTICAL line with the same thin recessed brown stone grout and ivory edge light seen throughout the original.
The vertical connector joins the already existing up-right diagonal ending at (627,727) to the already existing up-right diagonal starting at (627,756). These are TWO different parallel diagonal segments with a small vertical jog between them. They must both stay at their original coordinates: do not turn them into a single straight diagonal, do not regularize the diamond shape, and DO NOT move the adjacent gold vertex near (582,767), marked by the GREEN square. That gold vertex and every edge inside the green square must remain IDENTICAL to image 1. Magenta circles mark fixed endpoints, cyan marks only the new 29-pixel connector. The result will be an unusual little step, and that is required by the original map geometry.
Change only x619..637,y721..762. Keep all other existing grout including the long vertical at x627 y813..889 exactly unchanged. Same ivory hand-painted stone material and tiny lattice, no shifted corners, no global redraw, no blur, no added objects, no crop or zoom. Remove cyan, magenta and green locator ink. Native opaque 1254x1254 PNG.'''
args={'prompt':prompt,'referenced_image_paths':[str(base),str(guide)],'transparent_background':False};(D/'prompt.txt').write_text(prompt,encoding='utf-8');p.write_json(D/'parameters.json',args,replace=False)
ref=lambda f:{'file':str(f),'sha256':p.sha(f)}
p.write_json(D/'request.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'parameters':args,'route':'builtin_image_gen','references':[dict(ref(base),role='exact edit target'),dict(ref(guide),role='locator only not production art')],'worldBox':[19853,26776,21107,28030],'tileOrigins':{'r07_c05':[3469,2200],'r07_c06':[-627,2200]},'actualModel':None,'actualQuality':None,'paidAPIUsed':False,'sourceResampled':False,'priorAttemptForThisJunction':'shared-east-lower-03 failed by moving the protected gold vertex; second focused attempt'},replace=False)
print(D)
