from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:dict(path=p.as_posix(),sha256=sha(p))
def image(p):return np.array(Image.open(p).convert('RGB'))
north='cross_r05r06_c04_paving_north_a01'
old=Z/'guides'/f'{north}.native-crop.png'
joined=Z/'qa'/f'{north}_mask_v1'/'combined_native_crop.png'
mask=Z/'qa'/f'{north}_mask_v1'/'source_selection_mask.png'
m=np.array(Image.open(mask))
assert not m[850:1000,0:55].any()
assert np.array_equal(image(old)[850:1000,0:55],image(joined)[850:1000,0:55])
jobs=[
 ('cross_r06_c03c04_rail_ground_join_a01','v1','REJECTED_BOUNDARY','Central repair improved but new cutoff/doubled coarse contours at right and bottom mask boundary; never applied.'),
 ('cross_r06_c03c04_rail_ground_join_a01','v2','REJECTED_BOUNDARY','Right-bottom coarse node moved about 20px; wider mask still creates new boundary cuts near (1190,1050),(957,1195); never applied.'),
 ('cross_r05r06_c04_paving_left_joint_a01','v1','REJECTED_BOUNDARY','Left mask boundary truncates relocated coarse diagonal near (200,550); never applied.'),
 ('cross_r05r06_c04_paving_left_joint_a01','v2','OWNER_GEOMETRY_PASS','Expanded selection includes full left diagonal and coherent junction. Full1254 viewed; no new abrupt coarse contour cut. Already strict-applied in cross-v4.'),
 ('cross_r06_c03c04_rail_ground_join_a02','v1','OWNER_GEOMETRY_PASS','Two central blind coarse joints connect to continuous slabs or coherent T junctions. Full1254 viewed. Existing faint upper-right scratch intentionally unchanged; small-cell paving material remains pending. Not yet applied.')
]
items=[]
for stem,v,status,note in jobs:
 d=Z/'qa'/f'{stem}_mask_{v}'
 items.append(dict(stem=stem,selectionVersion=v,source=info(Z/'native'/f'{stem}.png'),combined=info(d/'combined_native_crop.png'),mask=info(d/'source_selection_mask.png'),selectionRecord=info(d/'mask_selection.json'),nativeViewed=[1254,1254],status=status,note=note))
out=Z/'qa/r05r06_two_followup_repairs_owner_review_20261013.json'
assert not out.exists()
data=dict(schemaVersion=1,createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='connected_continuation',scope='Native local geometry and hard-source boundaries only; whole map and material not accepted.',priorDefectEvidence=dict(priorTarget=info(old),priorCombined=info(joined),priorMask=info(mask),reportedOriginalCropPoint=[50,910],pointOutsideSelection=bool(m[910,50]==0),unchangedNativeBox=[0,850,55,1000],exactPixelsUnchanged=True,conclusion='The left-side blind grout end existed before paving_north repair and was outside its selection. New paving_left_v2 addresses it.'),items=items,formalAccepted=False,independentReviewPending=True)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(info(out)))

