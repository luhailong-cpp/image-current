import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *
import subprocess
ids={'bottle':'r03_c12_cross_03_03_bottle_paint_repair','left':'r03_c12_cross_02_04_gourd_paint_repair','right':'r03_c13_cross_02_01_gourd_paint_repair'}
expected={'r03_c12':'d9f3eb6247a0d903b7a3ef59c875ce4ec28dd7c60aa56f1d4d9c9f361169473a','r03_c13':'ef14184b97748121bc3437483f0cb23524547920ea2400918659a895677f114f'}
histories={}
for tid,h in expected.items():
 p=ZONE/'tiles'/f'{tid}.png';assert sha(p)==h
 hist=ZONE/'qa/history'/f'{h[:12]}-{tid}-before-color-repairs-20261011';assert not hist.exists();hist.mkdir()
 for src in [p,p.with_suffix('.png.derivation.json'),ZONE/f'selection-{tid}.json',ZONE/'qa'/f'{tid}-preview.png']:
  if src.exists():shutil.copy2(src,hist/src.name)
 shutil.copytree(ZONE/'qa'/f'{tid}-final',hist/f'{tid}-final')
 histories[tid]=hist.as_posix()
for key,ident in ids.items():
 p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p);q.update(status='passed_geometry_color_and_repair_perimeters',internalSeams='passed repair center and surrounding attachment edges at100pct',externalSeams='repair perimeter passed; formal whole-zone acceptance remains pending',reviewedAtUtc=now());write(p,q)
def overlay(oid,sourceid,crop,paste,world):
 src=ZONE/'native'/f'{sourceid}.png'
 q={'id':oid,'operation':'exact rectangular native repair core crop and paste; no resampling or feathering','source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':crop,'tileLocalPaste':paste,'worldPaste':world,'review':'passed_geometry_color_and_repair_perimeters','reviewedAtUtc':now(),'reviewerEvidence':'repair_prepare_local direct100pct inspection of core defect, all surrounding perimeter strips, and full object context','actualModel':None,'actualQuality':None}
 write(ZONE/'qa'/f'{oid}.overlay.json',q)
 return oid
o1=overlay(ids['bottle'],ids['bottle'],[115,115,1139,1139],[2560,2560],[47616,10752])
o2=overlay(ids['left'],ids['left'],[115,115,947,1139],[3264,1536],[48320,9728])
o3=overlay('r03_c13_cross_02_01_gourd_paint_bridge',ids['left'],[947,115,1139,1139],[0,1536],[49152,9728])
o4=overlay(ids['right'],ids['right'],[115,115,1139,1139],[192,1536],[49344,9728])
for tid,newids in [('r03_c12',[o1,o2]),('r03_c13',[o3,o4])]:
 p=ZONE/f'selection-{tid}.json';s=read(p);assert not any(i in s['overlays'] for i in newids);s['overlays']+=newids;s['priorRevision']=expected[tid];s['priorSelectionHistory']=histories[tid]+'/selection-'+tid+'.json';s['updatedAtUtc']=now();write(p,s)
 subprocess.run([sys.executable,str(ZONE/'assemble_tile.py'),tid],check=True)
write(ZONE/'qa/color-repairs-20261011-merge.json',{'status':'native_repairs_merged_pending_final_verification','createdAtUtc':now(),'oldTileHashes':expected,'histories':histories,'repairs':ids,'actualModel':None,'actualQuality':None,'formalAccepted':False})
