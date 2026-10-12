from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,uuid
T=Path(__file__).resolve().parent;Q=T/'review/root-native-full-qa-20261012'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
 tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
m=read(Q/'manifest.json');L=read(T/'candidate/latest-assembly.json')
assert L['candidate']['sha256']==m['candidate']['sha256']
assert len(m['images'])==53
for im in m['images']:assert sha(Path(im['path']))==im['sha256']
fail={'id':'I01','boxIn4096':[1090,0,1280,1160],'severity':'blocking','description':'False straight vertical stone/water material boundary around x1173 truncates two small leaves; apparent from v1024-q0/q1, h1024-q1, j1024-1024 and north q1.'}
extras={'id':'L01','boxIn4096':[800,490,1280,1010],'severity':'blocking','description':'Three small floating green leaves introduced in p01_01/left overlap are absent from the approved local layout. Two are clipped by I01. Remove within a true native local water repair, preserving approved leaf near x1900.'}
report={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidate':m['candidate'],'assembly':m['assembly'],'evidenceManifest':{'path':str(Q/'manifest.json'),'sha256':sha(Q/'manifest.json')},'actuallyViewedNativeEvidence':[dict(im,actuallyViewedAtOriginalPixelSize=True) for im in m['images']],'overviewRole':'preview only; all six seam bands, nine junctions, four edges and four west-core join quarters separately viewed without resize','fullSeamBands':6,'junctionCount':9,'edgeQuarterCount':16,'externalWestQuarterCount':4,'status':'failed_local_native_repair_required','internalSeamQA':'failed_I01','internalArtQA':'failed_I01_L01','findings':[fail,extras],'remainingInternalObservations':'Other five full seam bands and eight junctions show connected wood, finial, lotus petal/leaf outlines without duplicate structure or broken grout. Existing soft water/stone finish variations remain review notes, not RGB edits.','externalWestReview':{'neighborSha256':'173e67ac86c37595dd6ad272757093367dab48585f73c8192c832fcf3f42110f','status':'geometry_locally_connected_material_watch_not_formal','observations':'Wood plank/apron/post edges connect through q1-q3. q0 green inset paving changes fine texture/value at the join and remains under material watch; standalone strips do not establish external acceptance.'},'externalNorthSouth':'neighbor candidates unavailable; pending','externalEast':'outside artwork canvas; edge crop reviewed without a black frame','formalAccepted':False}
p=Q/'visual-qa.json'
if not p.exists():
 with p.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
p=read(T/'progress.json');p.update(status='full_native_QA_failed_local_shore_repair_in_progress',internalArtQA='failed_local_native_repair_required',internalSeamQA='failed_I01',rootNativeQA={'path':str(Q/'visual-qa.json'),'sha256':sha(Q/'visual-qa.json')},externalNeighborSeamQA='west_local_geometry_material_watch_north_south_pending_east_canvas_boundary',formalAccepted=False,nextStep='Fix x1173 false stone/water division and three unapproved clipped leaves with actual native repair; review changed native evidence before any pass.')
atomic(T/'progress.json',p);L.update(internalArtQA=p['internalArtQA'],internalSeamQA=p['internalSeamQA'],rootNativeQA=p['rootNativeQA'],formalAccepted=False);atomic(T/'candidate/latest-assembly.json',L)
print(json.dumps({'report':str(Q/'visual-qa.json'),'sha256':sha(Q/'visual-qa.json'),'viewedNativeCount':53,'formalAccepted':False}))
