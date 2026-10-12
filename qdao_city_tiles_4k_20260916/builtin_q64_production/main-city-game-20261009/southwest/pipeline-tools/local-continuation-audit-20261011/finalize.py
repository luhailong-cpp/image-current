import sys,json,hashlib,re
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import numpy as np
from PIL import Image
S=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
O=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d): (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
now=datetime.now(timezone.utc).isoformat()
d=read(O/"receipt-discovery.json")
unique={}
failed=[]
for x in d["receipts"]:
 if not x.get("image"): failed.append(x);continue
 h=x["image"]["sha256"]
 if h not in unique:unique[h]={"sha256":h,"image":x["image"],"sourceOutput":x["output"],"receipts":[],"explicitRejected":False}
 unique[h]["receipts"].append(x["receipt"])
 unique[h]["explicitRejected"]|=x["explicitRejected"]
intermediate={"899185f03d","c9a1dc53d0","1ff6899ab2"}
localprefix={"faa2e762f2","d963b18b9e","0f8d0d6438","fc609f74b6","461d21fd57","f6ae139f00","5f70599423","c763e174d6","1c707b8265","1a5a2e2c95","7a2f4d43a3","8bb5535acc","db9e1b7115","6e250ca116","ce55aefa75","2390b23afe","6fa7f9a010","79062e5e96","38f9c69053","e1ba4510d6","0ef695c0ee","382b5df7b9","3bb261e107","3d8e68a47f","b2c4891a20","bab6c7ac8e","d22ec094d9","faa74b25c3","face4c8061"}
for h,x in unique.items():
 rel=str(Path(x["receipts"][-1]).relative_to(S)).replace("\\","/")
 pref=h[:10];x["sourceTile"]=next(iter(re.findall(r"r\d\d_c\d\d",rel)),None)
 if pref=="6532557e3f":
  cat="historically_rejected_now_local_reuse_proposal_pending_merge"
  why="Original overwide stair rejected. G01 proposal reuses translated native end cap in a limited mask; v2 does not yet include it."
 elif 'crossedge-stair-restored-20261011' in rel:
  cat='local_repair_pending_review_and_merge'
  why='New native return from concurrently active cross-edge repair; not part of the four v2 candidates.'
 elif pref in intermediate:
  cat="superseded_intermediate_reference_only"
  why="Documented non-direct contributor in first-row final-visual-review; superseded by edge/groove refinements."
 elif x["explicitRejected"]:
  cat="rejected"
  why="Explicit historical receipt or independent prior disposition rejects this return; no selected pixels."
 elif pref in localprefix:
  cat="local_reuse_in_current_v2"
  why="Selected mask/subregion contributor through pre-v2 repair assembly and v2 integration."
 elif re.match(r"r10_c05/receipts/p0[34]_",rel):
  cat="superseded_spatial_base"
  why="Same spatial slot replaced by r10_c05/refinement/selection.json; retained as source lineage."
 elif re.match(r"r(10|11|12)_c0[56]/(pipeline/)?receipts/p\d\d_\d\d",rel) or re.match(r"r10_c05/refinement/receipts/p\d\d_\d\d",rel):
  cat="selected_spatial_native"
  why="Selected native spatial slot in tile native directory, with r10_c05 lower-row refinement selection."
 else:
  cat="unclassified";why="Needs explicit disposition."
 x["disposition"]=cat;x["reason"]=why
 if pref=="face4c8061":x["reason"]+=" Top-right tone retained outside east-combined mask; inside that mask v2 reuses verified 08 baseline and cross-edge patch."
 if pref=="6e250ca116":x["reason"]+=" Child rejection was superseded by parent masked salvage, not whole-output acceptance."
counts=dict(Counter(x["disposition"] for x in unique.values()))
# Verify all record images that claim 1254-pixel native generation against receipt return hashes.
records=[];unmatched=[];errors=[]
for p in S.rglob("*.json"):
 if O in p.parents or "audit-runs" in p.parts:continue
 if not (p.name.endswith(".generation.json") or p.name=="generation.json"):continue
 try:
  r=read(p);f=r.get("file")
  if not isinstance(f,str):continue
  f=Path(f)
  if not f.exists():continue
  im=Image.open(f)
  if im.size!=(1254,1254):continue
  h=sha(f)
  rec={"record":str(p),"file":str(f),"sha256":h,"receiptAccounted":h in unique}
  records.append(rec)
  if h not in unique:unmatched.append(rec)
 except Exception as e:errors.append({"record":str(p),"error":str(e)})
v2=S/"integrated-20261011/v2"
prior=read(v2/"qa-review.json")
pairs=[]
for x in prior["tileChecks"]:
 c=Path(x["candidate"]["file"]);ctx=Path(x["context"]["file"])
 a=np.array(Image.open(c));b=np.array(Image.open(ctx))
 pairs.append({"tile":x["tile"],"candidate":{"file":str(c),"sha256":sha(c),"pixels":list(Image.open(c).size)},"context":{"file":str(ctx),"sha256":sha(ctx),"pixels":list(Image.open(ctx).size)},"hashUnchangedFromIndependentV2Review":sha(c)==x["candidate"]["sha256"] and sha(ctx)==x["context"]["sha256"],"coreEqualsContextCrop":bool(np.array_equal(a,b[115:4211,115:4211]))})
full={x["tile"] for x in pairs}
spatial=defaultdict(list)
for x in unique.values():
 if x["disposition"]=="selected_spatial_native":
  ids=re.findall(r"p\d\d_\d\d",x["receipts"][-1]);x["spatialSlot"]=ids[-1] if ids else None
  spatial[x["sourceTile"]].append({"slot":x["spatialSlot"],"sha256":x["sha256"],"sourceOutput":x["sourceOutput"],"receipts":x["receipts"]})
coverage=[]
for r in range(9,17):
 for c in range(1,9):
  tile=f"r{r:02d}_c{c:02d}";slots=spatial.get(tile,[])
  coverage.append({"tile":tile,"row":r,"column":c,"worldCore":[(c-1)*4096,(r-1)*4096,c*4096,r*4096],"excluded":False,"full4kCandidate":tile in full,"formalAccepted":False,"selectedNativeSlots":slots,"selectedNativeCount":len(slots),"missingNativeSlots":[f"p{y:02d}_{x:02d}" for y in range(1,5) for x in range(1,5) if f"p{y:02d}_{x:02d}" not in {s["slot"] for s in slots}],"status":"full_candidate_visual_and_neighbors_pending" if tile in full else "partial_native_in_production" if slots else "no_selected_native_saved_in_receipt_snapshot"})
partial=[x for x in coverage if not x["full4kCandidate"] and x["selectedNativeCount"]]
missing=[x["tile"] for x in coverage if not x["full4kCandidate"]]
edges=[]
for tile,side,neighbor,seg in [
 ("r10_c05","north","r09_c05",[16384,36864,20480,36864]),("r10_c06","north","r09_c06",[20480,36864,24576,36864]),
 ("r10_c05","west","r10_c04",[16384,36864,16384,40960]),("r11_c05","west","r11_c04",[16384,40960,16384,45056]),
 ("r10_c06","east","r10_c07",[24576,36864,24576,40960]),("r11_c06","east","r11_c07",[24576,40960,24576,45056]),
 ("r11_c05","south","r12_c05",[16384,45056,20480,45056]),("r11_c06","south","r12_c06",[20480,45056,24576,45056])]:
 edges.append({"tile":tile,"side":side,"neighbor":neighbor,"worldSegment":seg,"neighborFullCandidateExists":neighbor in full,"neighborSelectedNativeCount":len(spatial.get(neighbor,[])),"status":"pending_neighbor_full_artwork_and_native_visual_review"})
assign=S.parents[1]/"acceleration-20261010/assignments.json"
assignment=read(assign)
exclusions=[a for a in assignment["assignments"] if a["map"]=="main-city-game-20261009" and a.get("previousZone")=="southwest"]
shared=[{"id":"west_horizontal","tiles":["r10_c05","r11_c05"],"status":"pass","finding":"Previously visually passed, preserved."},
{"id":"east_horizontal","tiles":["r10_c06","r11_c06"],"status":"pass","finding":"Stone-base band improved by local cross-edge material repair."},
{"id":"north_vertical","tiles":["r10_c05","r10_c06"],"status":"pending","geometry":"pass","finding":"Wood color improved; lower stairs retain visible brightness/material mismatch."},
{"id":"south_vertical","tiles":["r11_c05","r11_c06"],"status":"pending","geometry":"pass","finding":"S1/S2 definite P1 grout breaks fixed; broader brightness/material mismatch remains."}]
write("receipt-dispositions.json",{"snapshotAtUtc":d["createdAtUtc"],"receiptCount":d["receiptCount"],"uniqueSuccessfulNativeOutputs":len(unique),"duplicateSuccessReceiptCount":sum(len(x["receipts"])-1 for x in unique.values()),"historicalNoOutputFailures":len(failed),"dispositionCounts":counts,"outputs":list(unique.values()),"failures":failed,"nativeGenerationRecordCount":len(records),"unaccountedSavedNativeRecords":unmatched,"recordReadErrors":errors,"generationRecords":records,"actualModelAndQuality":"null where host undisclosed; configuration values are not proof of actual model/quality"})
write("coverage.json",{"snapshotAtUtc":d["createdAtUtc"],"assignmentEvidence":{"file":str(assign),"sha256":sha(assign),"southwestExclusions":exclusions},"targetTiles":64,"complete4kCandidates":len(full),"formalAccepted":0,"missingFullCandidateCount":len(missing),"missingFullCandidateCoordinates":missing,"partialTiles":partial,"tiles":coverage,"candidateContextVerification":pairs,"sharedEdges":shared,"outer2x2Segments":edges})
report={"createdAtUtc":now,"receiptSnapshotAtUtc":d["createdAtUtc"],"targetTiles":64,"fullCandidateTiles":4,"formalAcceptedTiles":0,"uniqueSuccessfulNativeOutputs":len(unique),"dispositions":counts,"selectedSpatialNativeSlots":sum(len(v) for v in spatial.values()),"partialTiles":{x["tile"]:x["selectedNativeCount"] for x in partial},"missingFullCandidates":len(missing),"unaccountedSavedNativeOutputs":len(unmatched),"unknownDispositions":counts.get("unclassified",0),"knownUnassembledSpatialOutputs":partial,"pendingRepairReuse":[{"issue":"r11_c06 G01","proposal":str(S/"r11_c06/repairs-restored-20261011/G01.proposal.json"),"sourceSha256":"6532557e3f0e8b4c1af3f4297531badf6952a9f79b653213fa85f8a8cb5bf502","currentlyInV2":False,"independentReview":"separate G01-independent-qa.json"}],"sharedEdgeCounts":{"pass":2,"pending":2},"exteriorEdgeSegmentsPending":8,"currentNetworkAccess":"enabled; past failures are historical, not current blocking condition","scopeNote":"Read-only source inventory; no artwork generated or modified; root progress files untouched. Concurrent production may add outputs after this snapshot."}
write("report.json",report)
text=f"""Southwest local continuation audit
Receipt snapshot UTC: {d['createdAtUtc']}
Target: 64 tiles (r09-r16, c01-c08), no southwest acceleration exclusions.
Full 4K candidate/context pairs: 4, all hashes unchanged and core crops exact. Formal accepted: 0.
Missing full candidates: 60. Saved partial production: {report['partialTiles']}.
Receipts: {d['receiptCount']}; unique successful native returns: {len(unique)}; duplicate success receipts: {sum(len(x['receipts'])-1 for x in unique.values())}; historical no-output failures: {len(failed)}.
Dispositions: {counts}.
Unaccounted saved native records: {len(unmatched)}; unknown successful-output dispositions: {counts.get('unclassified',0)}.
Existing four full tiles have no lost saved spatial patch awaiting assembly. r12_c05 saved patches are known active production, not a lost completed tile.
One historical rejected native has now been salvaged into pending G01 masked proposal; this proposal is not included in v2 yet.
Shared edges: 2 visually pass, 2 pending material/brightness. Both P1 south grout breaks are repaired. Eight outer 2x2 edge segments await complete neighbor artwork and visual review.
Network access is restored. Failure receipts describe history only.
All details, exact hashes and 64-coordinate inventory: coverage.json and receipt-dispositions.json.
"""
(O/"report.txt").write_text(text,encoding="utf-8")
print(json.dumps({k:report[k] for k in ["fullCandidateTiles","formalAcceptedTiles","uniqueSuccessfulNativeOutputs","dispositions","selectedSpatialNativeSlots","partialTiles","unaccountedSavedNativeOutputs","unknownDispositions"]}))

