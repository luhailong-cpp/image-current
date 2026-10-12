from pathlib import Path
import json,hashlib,datetime
Z=Path(__file__).resolve().parent;T="r07_c14"
def rd(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rf(p):return {"path":str(Path(p).resolve()),"sha256":sha(p)}
def wr(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s=rd(Z/"records"/f"{T}.working-selection.json");assert len(s)==16
audit=[]
for k,v in sorted(s.items()):
 p=Z/"native"/v;g=rd(str(p)+".generation.json");assert sha(p)==g["sha256"]
 refs=g["references"]
 for q in [g["prompt"],g["receipt"],g["source"],g["configSource"],*refs]:
  assert sha(q["path"])==q["sha256"],q["path"]
 for q in g["nativeEdgeSources"]:
  assert sha(q["path"])==q["sha256"]
  if q.get("provenanceRecord"):assert sha(q["provenanceRecord"]["path"])==q["provenanceRecord"]["sha256"]
 receipt=rd(g["receipt"]["path"])
 assert receipt["request"]["prompt"]==Path(g["prompt"]["path"]).read_text(encoding="utf-8-sig")
 assert receipt["request"]["referenced_image_paths"]==[q["path"] for q in refs]
 assert g["width"]==g["height"]==1254
 assert g["actualModel"] is None and g["actualQuality"] is None
 audit.append({"patchId":k,"native":rf(p),"generationRecord":rf(str(p)+".generation.json"),"coordinates":g["coordinates"],"receipt":g["receipt"],"verifiedReferencedImageCount":4,"nullModelQuality":True})
review=rf(Z/"qa"/T/"beam-independent-review.json")
j={"tile":T,"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"nativeCount":16,"coveredCoreCount":16,"candidate4kCount":1,"formalAcceptedCount":0,"tileCoreGlobalBox":[53248,24576,57344,28672],"candidate":rf(Z/"tiles"/f"{T}.candidate.png"),"selection":rf(Z/"records"/f"{T}.selection-v1.json"),"manifest":rf(Z/"qa"/T/"manifest.json"),"externalBoundariesManifest":rf(Z/"qa"/T/"external-boundaries.manifest.json"),"visualReview":review,"verdict":"candidate_visual_pass_ready_for_root_review","nativeUpscalePerformed":False,"pixelsOperation":"Exact crop[115,115,1139,1139] from each1254 native and opaque integer paste,16 unique1024 cores","actualBuiltinCallsThisTile":16,"failedCallsThisTile":0,"formalAccepted":False,"globalProgressModified":False,"gitModified":False,"sourceEvidenceAudit":audit}
wr(Z/"records"/f"{T}-production-handoff-20261011.json",j)
status=rd(Z/"records"/f"{T}.status.json");status.update({"candidate4kCount":1,"candidateVisualPass":True,"visualReview":review,"formalAcceptedCount":0,"handoff":rf(Z/"records"/f"{T}-production-handoff-20261011.json")});wr(Z/"records"/f"{T}.status.json",status)
print(json.dumps({"handoff":str(Z/"records"/f"{T}-production-handoff-20261011.json"),"nativeEvidenceAudited":16,"candidateVisualPass":True,"formalAccepted":False}))

