from pathlib import Path
import sys
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_s02_02_v01'
g=ROOT/'guides'/(stem+'.native-overlap-guide.png');layout=ROOT/'guides'/(stem+'.layout-only.png')
reqp=ROOT/'prompts'/(stem+'.request.json');req=p.load(reqp)
derivp=Path(str(g)+'.derivation.json');d=p.load(derivp)
original=p.metadata(g,'original prepared guide before conflicting right-halo exclusion')
box=[1024,230,1139,450]
with Image.open(g) as im, Image.open(layout) as lay:
 im.paste(lay.crop(box),box[:2]);im.save(g)
d['rightHaloExclusion']={'box':box,'reason':'Right source halo contains a clipped ball sliver inconsistent with the true accepted TOP sphere. Exclusion affects only neighbor halo x0..115; its actual core and remaining shaft constraints are preserved. Restore layout-only pixels in this small region so AI can continue the correct TOP sphere.','originalGuide':original,'layoutSource':p.metadata(layout,'restored layout-only region')}
d['sha256']=p.hashfile(g);p.dump(derivp,d)
req['references'][0]=p.metadata(g,'coordinate target with fixed TOP native sphere; RIGHT actual core fixed; conflicting ball sliver in RIGHT halo excluded to layout-only [1024,230,1139,450]')
req['rightHaloExclusion']=d['rightHaloExclusion'];p.dump(reqp,req)
print(req['references'][0])

