from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent;S=T.parent/'r07_c05/bridges/shared-east-lower-02';C=T/'repair-batches/c4-upper-material-01';D=T/'qa/restart-integration-20261013';D.mkdir(exist_ok=True)
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def wj(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
wj(D/'shared-lower-independent-review.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/finish_r07_c06','source':ref(S/'native.png'),'proposal':ref(S/'two-tile-proposal.json'),'actuallyViewed':[dict(**ref(S/f),detail='original',verdict='passed_local_scope') for f in ['repair-detail.png','upper-perimeter.png','lower-perimeter.png','left-perimeter.png','right-perimeter.png']],'finding':'The 50px vertical closure connects both diagonal tips without an open end. Four ROI perimeters retain continuous grout and stone grain. Scope is only source ROI [590,473,678,596]; other west-edge defects remain pending.','approvedRightSourceROI':[627,473,678,596],'approvedRightTileROI':[0,2673,51,2796],'approvedSharedSourceROI':[590,473,678,596],'formalAccepted':False})
wj(D/'c4-upper-independent-review.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/finish_r07_c06','source':ref(C/'native.png'),'proposal':ref(C/'trial-upper-band.json'),'actuallyViewed':[dict(**ref(C/f),detail='original',verdict='passed_local_scope') for f in ['upper-band.png','top-band.png','left-band.png','bottom-band.png']],'finding':'The hard horizontal grain cut at tile y909 has been replaced with continuous graded grain on each stone. Grout crossings are retained; source ROI perimeter has no confirmed clipping or horizontal band. This does not repair the separate upper c3/c4 grout gap around tile (3072,572..632).','approvedSourceROI':[115,571,1254,700],'approvedTileROI':[2957,853,4096,982],'formalAccepted':False})
pair=Image.open(S/'trial-native-roi.png').convert('RGB')
for y in [215,395,737,814,1090]:pair.crop((537,max(0,y-65),717,min(1254,y+115))).save(D/f'west-lower-y{y:04}.png')
wj(D/'west-lower-detail-crops.json',{'source':ref(S/'trial-native-roi.png'),'worldOrigin':[19853,26776],'tileOrigin':[-627,2200],'boundaryNativeX':627,'crops':[{'file':str(D/f'west-lower-y{y:04}.png'),'nativeLTRB':[537,max(0,y-65),717,min(1254,y+115)]} for y in [215,395,737,814,1090]]})
