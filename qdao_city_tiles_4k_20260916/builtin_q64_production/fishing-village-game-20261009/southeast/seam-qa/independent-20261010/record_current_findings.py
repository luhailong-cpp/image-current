import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
now=datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
repair=HERE/'repair-candidates'
p=repair/'east-deck-joint-v2.png.generation.json'
d=json.loads(p.read_text())
d['initialVisualReview']={'interior':'Original x32768 hard plank discontinuity replaced by coherent staggered butt joints.','boundaryWarning':'Central [115,115,1139,1139] adoption remains geometrically invalid at right and bottom edges; see perimeter-review.json.','candidateAdoptable':False}
write(p,d)
write(repair/'perimeter-review.json',{'reviewedAtUtc':now,'reviewer':'seam_review','selected':False,'formalAccepted':False,'candidateAdoptable':False,'candidate':str(repair/'east-deck-joint-v2.png'),'candidateSha256':sha(repair/'east-deck-joint-v2.png'),'globalBox':[32200,37888,33454,39142],'testedAdoptionGlobal':[32315,38003,33339,39027],'evidence':str(repair/'v2-adoption-preview/manifest.json'),'evidenceSha256':sha(repair/'v2-adoption-preview/manifest.json'),'edgeReview':{'top':'Bench legs, masonry and stone joint contours align. Minor tone change.','left':'Wood plank gap endpoints largely align; rectangular tone step remains.','right':'Multiple plank-gap endpoints jump roughly 20–40 pixels at world x33339, y38550–39027. Structural adoption blocker.','bottom':'Diagonal plank gap terminates against horizontal adoption boundary near world y39027, x32620–32880. Structural adoption blocker.'},'decision':'Preserve as unselected comparison. Do not adopt the rectangular crop, and do not claim color correction can resolve geometric endpoint mismatch. No third generation authorized in this review.'})
folder=HERE/'r11_c08'
native=json.loads((folder/'manifest.json').read_text())
lastsix=['p33--p34','p33--p43','p34--p44','p41--p42','p42--p43','p43--p44']
colorids=lastsix+[f'cross-r{r}-c{c}' for r in range(1,4) for c in range(1,4)]+['p22--p23','p24--p34']
colorfolder=BASE/'r11_c08/qa/color-full'
evidence=[]
for rec in native['results']:
 rid=rec['id']
 if rid not in lastsix and not rid.startswith('cross'):
  evidence.append({'id':rid,'variant':'native','file':rec['image']['file'],'sha256':rec['image']['sha256'],'geometry':'pass'})
for rid in colorids:
 f=colorfolder/(rid+'.png')
 evidence.append({'id':rid,'variant':'colorpass','file':str(f),'sha256':sha(f),'geometry':'pass'})
candidate=colorfolder/'candidate-4096.png'
report={'tile':'r11_c08','reviewedAtUtc':now,'reviewer':'seam_review','candidate':str(candidate),'candidateSha256':sha(candidate),'geometryPass':True,'reviewCoverage':{'uniqueInternalEdges':24,'uniqueIntersections':9,'method':'18 native edge strips plus 6 color edge strips and all 9 color intersections; color S1/S2 additionally re-viewed. Exact replay of all 16 RGB fields proves no geometry resampling/blur between native and color candidates.'},'colorReplay':str(folder/'independent-color-replay.json'),'colorReplaySha256':sha(folder/'independent-color-replay.json'),'structuralBlockers':[],'shadowObservations':[{'id':'S1','worldBox':[30680,41700,30830,42480],'objects':'Hull plank surfaces behind ladder','evidence':['p22--p23','cross-r1-c2'],'status':'Unresolved shadow-shape observation; vertical/stepped dark boundary remains after color pass. Plank gaps and ladder silhouette are continuous. Do not label bounded RGB correction as shadow geometry repair.'},{'id':'S2','worldBox':[32625,42945,32700,43080],'objects':'Stone paving just right of the sloping cradle support foot','evidence':['p24--p34'],'status':'Unresolved vertical shadow cutoff near world x32652. Stone outlines continue across it; not a core-edge contour break.'}],'nonblockingShapeObservation':{'id':'R1','worldBox':[30790,44310,30950,44950],'object':'Two foreground railing members','status':'Both members bend in a consistent direction around 100 pixels inside p43, away from core boundary. Continuous contours and wood thickness; acceptable whole-object curvature, no narrow seam repair requested.'},'formalAccepted':False,'internalReadyDecision':'Geometry permits continued expansion. Owner must preserve S1/S2 shadow observations when deciding candidate status; this report does not claim those observations resolved.','evidence':evidence}
write(folder/'final-geometry-review.json',report)
write(HERE/'external-open-issues.json',{'reviewedAtUtc':now,'formalAccepted':False,'issues':[{'id':'G2','classification':'structural blocker','worldBox':[32600,38190,32950,39027],'sharedBoundaryX':32768,'objects':'Wood floor plank gaps at r10_c08 east / r10_c09 west','sourceEvidence':str(HERE/'east-deck-focus/full-joint-input-100pct.png'),'sourceEvidenceSha256':sha(HERE/'east-deck-focus/full-joint-input-100pct.png'),'affectedSources':['r10_c08 p24','r10_c08 p34','r10_c09 p21','r10_c09 p31'],'status':'Original selected sources remain unchanged. v1 and v2 candidates unselected due adoption endpoint mismatch.'},{'id':'C2','classification':'shadow/tone boundary, external closure pending','worldBox':[32330,40700,32410,41100],'objects':'Wood floor at right edge of bench-rim repair','status':'Bench structural geometry pass remains valid. Root observed rectangular shadow/tone cutoff once r11_c08 north neighbor was connected; external closure remains pending.','reportedBy':'root','evidence':str(BASE/'seam-qa/r11_c08/north-segment-4-100pct.png')}]})
print(json.dumps({'written':['perimeter-review.json','r11_c08/final-geometry-review.json','external-open-issues.json'],'r11c08EvidenceCount':len(evidence)}))
