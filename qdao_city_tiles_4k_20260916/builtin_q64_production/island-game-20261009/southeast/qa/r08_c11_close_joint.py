from pathlib import Path
import os,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=R/'native/r08_c11_roof_joint_v01.png';d=rd(Q/'roof-joint-core-trial.json');d.update({'status':'candidate_complete_object_geometry_pass','reviewedAt':datetime.now(timezone.utc).isoformat(),'findings':['Whole gold scroll, lower sweeping hook, cladding and red ridge now form connected objects; old doubled cap and displaced interior silhouette removed.','Top stone material/edge, lower blue roof, actual fixed east edge and p43 left-lower contact directly viewed at original pixels. No new strong material bar or disconnected outline.','Minor painted surface variation and small local collar/shadow variation remain; no repeat generation planned for these.','Left-upper context-only strip remains pending the not-yet-generated p33; no formal external acceptance.'],'directEvidenceViewed':['top','bottom','right','left-lower','old-join'],'formalAccepted':False});wr(Q/'roof-joint-core-review.json',d)
f=R/'selected-native-r08_c11.json';s=rd(f);s['selected']['r08_c11_p34']='r08_c11_p34_v01.png';s['requiredOverlay']='selected-overlays-r08_c11.json';wr(f,s)
wr(R/'selected-overlays-r08_c11.json',{'tile':'r08_c11','overlays':[{'file':str(j),'sha256':sh(j),'originInTile':[2957,2413],'sourceCrop':[115,115,1139,1139],'destinationBox':[3072,2528,4096,3552],'review':str(Q/'roof-joint-core-review.json')}],'formalAccepted':False})
p=R/'progress-r08_c11.json';d=rd(p);d.update({'status':'repair_reviewed_continue','selectedNativeCount':5,'selectedOverlayCount':1,'inFlight':False,'nextStep':'p33 anchors exact selected cores plus accepted joint overlay; then continue row3 leftward.','lastReview':str(Q/'roof-joint-core-review.json')});wr(p,d)
