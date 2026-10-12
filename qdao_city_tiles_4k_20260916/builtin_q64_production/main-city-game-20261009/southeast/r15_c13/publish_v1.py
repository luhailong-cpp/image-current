from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,uuid
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p=Path(p);tmp=p.with_name(p.name+"."+uuid.uuid4().hex+".tmp")
 tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
 os.replace(tmp,p)
now=datetime.now(timezone.utc).isoformat()
idx=read(T/"candidate/latest-assembly.json")
q=T/"review/native-qa-20261011"
ver=read(q/"verification.json")
review=T/"review/assembly-e8d644ce11db9d4b4b84"
evidence=[{"path":str(p),"sha256":sha(p),"scale":"native pixel evidence"} for p in sorted(q.glob("*.png"))]
evidence.extend({"path":str(p),"sha256":sha(p),"scale":"native pixel crop"} for p in sorted(review.glob("junction-*.png")))
findings=[
 {"id":"north-material-band","status":"pending_not_passed","severity":"visible_material_discontinuity","tileBox":[0,0,3072,160],"description":"Full north joint inspected in four native 1024x800 segments. Wood and cream-gold roof contours largely align, but a straight horizontal texture/value change is visible at tile y=0, particularly x0..70 and roof x1100..3000. Keep immutable r14_c13 v6 unchanged; repair new side only."},
 {"id":"internal-stone-relief-termination","status":"minor_local_repair_pending","severity":"small_decorative_line_discontinuity","tileBox":[1840,3150,2080,3230],"description":"At junction x2048/y3072, the shallow upper inset border on the stone railing panel fades/terminates near tile x1955,y3175. Major cap, post, walkway and structural contours remain continuous. Do not mark all internal finish passed."},
 {"id":"other-neighbor-joints","status":"not_joint_reviewed","edges":["east","south","west"],"description":"All four standalone outer edges inspected at native pixels; east/south/west require neighboring current candidates for full joint acceptance."}
]
qa={"tile":"r15_c13","reviewedAt":now,"candidate":idx["candidate"],"context":idx["context"],"manifest":idx["manifest"],"formalAccepted":False,
 "reviewScope":{"fullVerticalSeams":3,"fullHorizontalSeams":3,"junctions":9,"standaloneEdges":4,"northJointLength":4096,"nativeScale":True},
 "internalArtQA":"structure_continuity_passed_with_minor_stone_relief_finish_pending",
 "externalNeighborSeamQA":"north_material_band_pending; east_south_west_joint_pending",
 "findings":findings,"evidence":evidence,"pixelReplay":ver["savedAlphaIndependentReplay"]}
write(q/"visual-qa.json",qa)
active=read(T/"active-native-map.json")
sources=[]
for p in sorted((T/"native").glob("*.png")):
 rec=read(str(p)+".generation.json")
 sources.append({"path":str(p),"sha256":sha(p),"logicalPatch":rec["logicalPatch"],"active":active.get(rec["logicalPatch"])==rec["id"],"actualSize":[rec["width"],rec["height"]],"resized":False})
handoff={"tile":"r15_c13","updatedAt":now,"status":"candidate_completed_pending_boundary_and_minor_finish_repair","candidate":idx["candidate"],"context":idx["context"],"manifest":idx["manifest"],"nativeActualOutputCount":len(sources),"activeNativeCount":len(active),"missingNativeCount":16-len(active),"sources":sources,"QA":{"path":str(q/"visual-qa.json"),"sha256":sha(q/"visual-qa.json")},"verification":{"path":str(q/"verification.json"),"sha256":sha(q/"verification.json")},"formalAccepted":False,"remaining":findings,"generationNeededCoordinates":[{"tile":"r15_c13","box":[0,0,3072,250],"purpose":"north boundary new-side texture continuity; preserve r14 core"},{"tile":"r15_c13","box":[1840,3150,2080,3230],"purpose":"small railing relief border completion"}],"noGitOperations":True,"noGameOrCapacityTests":True,"immutableNorthCore":{"path":str(T.parent/"r14_c13/candidate/r14_c13-4k-north-v6.png"),"sha256":"f1d683133fa23f466621f492375b55848d2a8c5775e039f10c2c86bc3860fda5"}}
assert sha(handoff["immutableNorthCore"]["path"])==handoff["immutableNorthCore"]["sha256"]
write(T/"handoff-r15_c13-20261011.json",handoff)
write(T/"local-continuation-20261011.json",handoff)
progress=read(T/"progress.json")
progress.update(status=handoff["status"],updatedAt=now,nativeActualOutputCount=len(sources),activeNativeCount=16,formalAccepted=False,internalArtQA=qa["internalArtQA"],externalNeighborSeamQA=qa["externalNeighborSeamQA"],visualQA=handoff["QA"],verification=handoff["verification"],remainingQA=findings,nextStep="Repair north texture band only on new tile side; complete small railing relief line; neighbor joint reviews pending.")
write(T/"progress.json",progress)
idx.update(status=handoff["status"],formalAccepted=False,internalArtQA=qa["internalArtQA"],externalNeighborSeamQA=qa["externalNeighborSeamQA"],visualQA=handoff["QA"],nativeActualOutputCount=len(sources),activeNativeCount=16,remainingQA=findings)
write(T/"candidate/latest-assembly.json",idx)
round=read(T/"continuation-round-20261011.json")
round.update(updatedAt=now,currentCoordinate="r15_c13",status=handoff["status"],activeNativeCount=16,nativeActualOutputCount=len(sources),candidate=idx["candidate"],context=idx["context"],manifest=idx["manifest"],QA=handoff["QA"],remainingQA=findings,nextStep=progress["nextStep"],currentBlockingServiceError=None)
write(T/"continuation-round-20261011.json",round)
print(json.dumps({"nativeActualOutputCount":len(sources),"candidate":idx["candidate"],"context":idx["context"],"manifest":idx["manifest"],"QA":handoff["QA"],"handoff":str(T/"handoff-r15_c13-20261011.json")},indent=2))

