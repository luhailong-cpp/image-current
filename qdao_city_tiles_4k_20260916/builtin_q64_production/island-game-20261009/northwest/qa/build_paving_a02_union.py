from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(__file__).resolve().parent.parent
Q=Z/'qa/repair_paving_a02_union_mask-v1';assert not Q.exists();Q.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
target=Z/'guides/r03_c03_repair_paving_a02.native-crop.png'
repair=Z/'native/r03_c03_repair_paving_a02.png'
old=np.asarray(Image.open(target).convert('RGB'));new=np.asarray(Image.open(repair).convert('RGB'))
assert old.shape==new.shape==(1254,1254,3)
assert sha(target)=='8f85a1aa0b06f51488bc504fe55e47e3f6a46ddc21a92f06f632b0bfb36d5216'
assert sha(repair)=='54772d1fb411bfd96d49602735924c2e8d15ac7df57af7650c154660ea0c86e0'
components=[];masks=[]
for n in (1,2):
 d=Z/f'qa/repair_paving_a02_node{n}_mask-v1';p=d/'source_selection_mask.png';a=np.asarray(Image.open(p).convert('L'));assert set(np.unique(a))<={0,255}
 record=d/'mask_selection.json';r=json.loads(record.read_text(encoding='utf-8'))
 assert r['target']['sha256']==sha(target) and r['repair']['sha256']==sha(repair)
 components.append(dict(path=p.as_posix(),sha256=sha(p),selectionRecord=dict(path=record.as_posix(),sha256=sha(record))))
 masks.append(a==255)
assert not (masks[0]&masks[1]).any()
mask=masks[0]|masks[1];combined=np.where(mask[...,None],new,old)
assert np.array_equal(combined[mask],new[mask]) and np.array_equal(combined[~mask],old[~mask])
mp=Q/'source_selection_mask.png';jp=Q/'combined_native_crop.png'
Image.fromarray(mask.astype('uint8')*255).save(mp);Image.fromarray(combined).save(jp)
rec=dict(operation='disjoint Boolean union of two hard same-coordinate source-selection masks',components=components,target=dict(path=target.as_posix(),sha256=sha(target)),repair=dict(path=repair.as_posix(),sha256=sha(repair)),mask=dict(path=mp.as_posix(),sha256=sha(mp),zeroSource='target',value255Source='repair'),combinedCrop=dict(path=jp.as_posix(),sha256=sha(jp),nativeSize=[1254,1254]),repairPixelCount=int(mask.sum()),targetPixelCount=int((~mask).sum()),resizing=False,registration=False,feathering=False,colorCorrection=False,pixelSynthesis=False,isAiGeneration=False,exactSourceProvenanceAsserted=True,visualStatus='pending_native_boundary_review')
(Q/'mask_selection.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n,box in [('node1_complete_boundary100pct',[80,120,525,500]),('node2_complete_boundary100pct',[740,130,1090,475])]:
 Image.fromarray(combined).crop(box).save(Q/(n+'.png'))
print(json.dumps(dict(mask=mp.as_posix(),maskSha256=sha(mp),combined=jp.as_posix(),combinedSha256=sha(jp),repairPixels=int(mask.sum()))))
