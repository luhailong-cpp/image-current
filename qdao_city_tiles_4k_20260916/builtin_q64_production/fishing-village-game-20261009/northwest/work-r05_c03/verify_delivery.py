from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parent;F=W/'final-v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
 p=Path(p);tmp=p.with_name(p.name+'.writing');tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
a=read(F/'assembly.json');expected=np.asarray(Image.open(a['candidate']['file']).convert('RGB'))
ids=np.asarray(Image.open(a['sourceIdMap']['file'])).astype(np.uint16)
out=np.zeros((4096,4096,3),dtype=np.uint8);covered=np.zeros((4096,4096),bool)
count=[]
for s in a['sources']:
 assert sha(s['file'])==s['sha256']
 assert sha(s['generationRecord'])==s['generationRecordSha256']
 g=s['globalNativeBox'];src=np.asarray(Image.open(s['file']).convert('RGB'))
 yy,xx=np.nonzero(ids==s['sourceId']);sy=yy+16384-g[1];sx=xx+8192-g[0]
 assert ((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)).all()
 out[yy,xx]=src[sy,sx];covered[yy,xx]=True
 count.append({'sourceId':s['sourceId'],'pixels':int(xx.size)})
assert covered.all()
bad=int(np.any(out!=expected,axis=2).sum());assert bad==0
ind={'method':'independent reconstruction using only saved source-ID map and source registry global coordinates; no composition helper imported','pixels':16777216,'pixelMismatches':bad,'uncoveredPixels':int((~covered).sum()),'candidateSha256':sha(a['candidate']['file']),'sourceIdSha256':sha(a['sourceIdMap']['file']),'sources':count,'resampled':False,'feathered':False}
write(F/'independent-replay.json',ind)
inspected=[]
for kind,pattern in [('whole-tile-core','core-*.100pct.png'),('internal-seam','h*.100pct.png'),('internal-seam','v*.100pct.png'),('internal-junction','junction-*.100pct.png'),('repair-entire-frame-and-mask-perimeter','*-whole-after.100pct.png')]:
 for p in sorted((F/'qa').glob(pattern)):
  inspected.append({'file':str(p),'sha256':sha(p),'kind':kind,'inspectionScale':'100 percent native pixels','status':'pass','finding':'No broken silhouette, artificial rectangular seam or detached rope terminal observed.'})
for j in range(1,5):
 p=F/f'qa/north-{j}.100pct.png';q=W/f'stage-bridge/qa/north-{j}.100pct.png'
 assert sha(p)==sha(q)
 inspected.append({'file':str(p),'sha256':sha(p),'kind':'existing-north-neighbor-shared-boundary','inspectionScale':'100 percent native pixels','status':'pass','finding':'Rope contours, mesh, sand and main pole continue across global y16384; final crop is byte-identical to inspected stage-bridge crop.'})
assert len(inspected)==55
qa={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'north_joint_resume','tile':'r05_c03','status':'pass-whole-tile-native-geometry-and-existing-north-boundary','inspectedCounts':{'wholeTile1024Cores':16,'internalSeamSegments':24,'internalJunctions':9,'repairFramesIncludingAllMaskPerimeters':2,'northSharedBoundarySegments':4},'inspected':inspected,'northNeighbor':{'file':str(B/'delivery-2x2/stage-v3/r04_c03.png'),'sha256':sha(B/'delivery-2x2/stage-v3/r04_c03.png')},'resolvedFindings':[{'id':'blue-cut-end','repair':'r05_c03_net_corner_bridge_v01','result':'Blue upper-bound edge now terminates as a wrapped round knot on its support rope.'},{'id':'cream-cut-end','repair':'r05_c03_cream_edge_bridge_v01','result':'The left cream border is one continuous curved hem; dangling extra terminal removed.'},{'id':'lantern-sand-straight-band','repair':'r05_c03_s04_s01_v02','result':'Straight y230 texture/lighting divide removed while lantern support geometry remains fixed.'}],'openAdjacentBoundaryWork':['west: neighboring r05_c02 not yet provided','east: neighboring r05_c04 not opened per scope','south: neighboring r06_c03 not yet provided'],'noUnreviewedExistingNorthDefects':True,'formalAccepted':False}
write(F/'visual-review.json',qa)
a['status']='native-tile-complete-full-geometry-and-existing-north-QA-passed'
a['visualQA']={'file':str(F/'visual-review.json'),'sha256':sha(F/'visual-review.json')}
a['independentReplay']={'file':str(F/'independent-replay.json'),'sha256':sha(F/'independent-replay.json')}
write(F/'assembly.json',a)
delivery={'tile':'r05_c03','status':a['status'],'globalCoreBox':[8192,16384,12288,20480],'dimensions':[4096,4096],'candidate':a['candidate'],'sourceIdMap':a['sourceIdMap'],'assembly':{'file':str(F/'assembly.json'),'sha256':sha(F/'assembly.json')},'sources':len(a['sources']),'selectedGridFragments':16,'independentReplay':a['independentReplay'],'visualQA':a['visualQA'],'nativeGenerationOutputsForTile':len(list((B/'native').glob('r05_c03*.png'))),'actualModel':None,'actualQuality':None,'nativeRGBOnly':True,'resample':False,'feather':False,'adjacentExistingTileDeltas':[],'adjacentExistingTilePixelsModified':False,'rootIndicesModified':False,'formalAccepted':False,'pending':'Root integration/review; future west/east/south neighbor boundary review when those tiles exist.'}
write(W/'delivery.json',delivery)
p=read(W/'progress.json');p.update(status=delivery['status'],selectedCandidateFragments=16,generationOutputs=delivery['nativeGenerationOutputsForTile'],inFlight=False,lastSelected='r05_c03_s04_s04_v01',delivery=str(W/'delivery.json'),next='Root integration; do not open r05_c04 without assignment');write(W/'progress.json',p)
pending=W/'qa/r05_c03_s03_s02_v01.pending-findings.json';q=read(pending);q['status']='resolved-by-local-native-bridge-in-final-v1';q['resolution']=str(F/'visual-review.json');write(pending,q)
print(json.dumps(delivery))

