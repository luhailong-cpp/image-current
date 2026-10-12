import sys,json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
tile=Path(__file__).resolve().parents[2];zone=tile.parent
spec=importlib.util.spec_from_file_location('production_v2',zone/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
identifier=sys.argv[1];out=tile/'qa'/'resume20261012'/identifier
manifest=p.read(out/'crop-manifest.json')
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':manifest['source'],'actuallyViewed':True,'viewDetail':'original','viewedNative':True,'viewedCrops':manifest['crops'],'status':'passed_available_source_adoption','notes':'Native1254 image and exact north/west core seams plus northwest junction inspected. Existing outlines connect and material variation is continuous.','fullTileInternalQA':False,'formalAccepted':False}
path=out/'review.json';p.write_json(path,review)
selection=p.record_selection('r05_c07',identifier[:6],identifier,'Native1254 and available exact north/west joins and northwest junction inspected; source usable, full tile QA pending.',path)
print(json.dumps(selection))
if len(sys.argv)>2:
 result=p.prepare('r05_c07',sys.argv[2],'resume01','north,west')
 print(json.dumps({k:result[k] for k in ['guide','nativeAnchors','missingNeighborSlots']}))
