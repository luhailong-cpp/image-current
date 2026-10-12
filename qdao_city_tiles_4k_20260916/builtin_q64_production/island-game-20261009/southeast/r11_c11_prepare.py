from pathlib import Path
from PIL import Image
import numpy as np, runpy, sys
from workflow import ROOT, read, write, sha, now
qa=ROOT/'qa'/'r11_c12-left-independent-v02'; qa.mkdir(exist_ok=True)
candidate=ROOT/'tiles'/'r11_c12.candidate-v02.png'
im=Image.open(candidate).convert('RGB'); assert im.size==(4096,4096)
im.resize((1024,1024),Image.Resampling.LANCZOS).save(qa/'whole-preview.png')
index=read(ROOT/'qa'/'r11_c12-v02'/'qa-index.json')
checks=[]
for e in index['seams']+index['junctions']+index['repairBoundaries']:
 p=Path(e['file']); actual=im.crop(e['sourceCrop'])
 assert sha(p)==e['sha256']
 assert np.array_equal(np.array(actual),np.array(Image.open(p).convert('RGB')))
 checks.append({'id':e['id'],'file':str(p),'sha256':sha(p),'candidateCropExact':True,'visuallyViewed':not e.get('identicalToV01',False)})
report={'tile':'r11_c12','candidate':str(candidate),'sha256':sha(candidate),'reviewer':'left_continue independent reviewer','reviewedAt':now(),'status':'independent_changed_geometry_and_boundaries_pass','checkedCandidateCrops':checks,'changedSeamsViewed':['h31','h41','v21','v22','v31','v32'],'changedJunctionsViewed':['junction_21','junction_31'],'repairBoundaryCountViewed':8,'findings':[],'observations':['Rail upper and lower edges continue without the former step; post connections are coherent.','Deck rim and long plank joints maintain the same slope through old cut and both repair side boundaries.','Stone joints and water reflections remain coherent through the two changed intersections.'],'inheritedSourceAudit':str(ROOT/'qa'/'r11_c12-v02'/'source-audit.json'),'formalAcceptedCount':0,'limitations':['Review is of the changed internal seams and repair perimeter; southern external neighbor is not built.']}
write(qa/'review.json',report)
sys.argv=['prepare_tile.py','r11_c11'];runpy.run_path(str(ROOT/'prepare_tile.py'),run_name='__main__')
p=ROOT/'progress-r11_c11.json'
if not p.exists():write(p,{'tile':'r11_c11','updatedAt':now(),'status':'guides_ready','generatedNativeCount':0,'usableNativeCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'nextStep':'Generate p14 then extend left and downward using true north/east neighbors.'})
tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']=='r11_c11')
print(tile)
# Guide previews only: no final pixels created here.
with Image.open(read(ROOT/'references.json')[0]['file']) as layout:
 boxes=[p['layoutReferenceBox'] for p in tile['patches']]
 box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
 layout.transform((1024,1024),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(ROOT/'qa'/'r11_c11.layout-preview.png')
for tid,v in [('r10_c11','v03'),('r11_c12','v02')]:
 Image.open(ROOT/'tiles'/f'{tid}.candidate-{v}.png').resize((1024,1024),Image.Resampling.LANCZOS).save(ROOT/'qa'/f'{tid}.r11c11-neighbor-preview.png')
