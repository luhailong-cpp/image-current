from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
choices=[
['s01_01_a04','s01_02_a03','s01_03_a03','s01_04_a03'],
['s02_01_a04','s02_02_a03','s02_03_a01','s02_04_a02'],
['COMPOSITE','s03_02_a03','s03_03_a01','s03_04_a04'],
['s04_01_a01','s04_02_a02','s04_03_a01','s04_04_a01']]
matrix=[]
for row in choices:
 out=[]
 for stem in row:
  if stem=='COMPOSITE':
   rel='qa/s03_01_native_composite_a01_base_a04_beam/candidate.png'
   entry=dict(path=rel,nativeCompositeRecord='qa/s03_01_native_composite_a01_base_a04_beam/native_composite_record.json')
  else:
   rel='native/r03_c03_'+stem+'.png';entry=dict(path=rel,generationRecord=rel+'.generation.json')
  p=Z/rel;assert p.is_file(),str(p)
  entry['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();out.append(entry)
 matrix.append(out)
manifest=dict(schemaVersion=1,tileId='r03_c03',nativePixels=1254,corePixels=1024,haloPixels=115,patchMatrix=matrix,status='diagnostic_candidate_pending_full_native_review',knownReviewItems=['row3 col3 firework silhouette and ornament against bottom native','row3/4 col4 duplicated stone joint near native x695','row3/4 col3-col4 and col2-col3 four-source intersections'])
p=Z/'r03_c03.candidate-v1.manifest.json';assert not p.exists()
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p.as_posix())

