import json,hashlib,datetime
from pathlib import Path
s=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
reports=[]
for tile,version in [("r14_c15","north-board-joint-20261012-v1"),("r14_c14","north-far-east-ledges-20261012-v1")]:
 d=s/tile/"repairs"/version;m=json.loads((d/"composition.json").read_text())
 ev=[dict(e,actuallyViewedAtOriginalPixelSize=True,status="pass_observed") for e in m["QAImages"]]
 o={"schemaVersion":1,"reviewer":"assembly_support","reviewedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"candidate":m["candidate"],"manifest":info(d/"composition.json"),"native":m["native"],"receipt":m["receipt"],"replay":m["replay"],"sourceNativeActuallyViewed1254":True,"evidence":ev,"status":"local_visual_pass_pending_root_review","publishedByReviewer":False,"formallyAccepted":False,"RGBColorCorrection":False,"resampling":False}
 if tile=="r14_c15":
  o["findings"]=["The existing x230 vertical deck joint now crosses the fixed north-core boundary continuously and ends at the original diagonal plank groove.","All four saved-alpha boundaries retain wood grain, bevel geometry and lighting without an observed cut or double groove.","The 7879 changed pixels are confined to [195,0,269,109]. Existing internal 6-seam/9-junction visual pass is unchanged; west y1090/2278/3515 defects remain unchanged."]
  o["northJoin"]="N01 locally resolved on 5ce10046; other three previously viewed north core quarters are pixel-identical. Root review required before publishing or changing selection."
  o["remainingExternal"]="West W01-W04 failed; east/south full-neighbor joins remain pending."
 else:
  o["findings"]=["Upper platform bevel and broad shadow continue across the fixed north core into the new side, including x3532..3892; no former straight shadow cutoff observed.","Both horizontal wood levels, lower bright ledge rim, left upright, legs and paving remain present and aligned. Three shaped lower-alpha-boundary segments have no observed hard cut or duplicate outline.","The far-right true-core join against current r14c15 3f0 at y0..1024 was independently viewed; no new geometry break observed.","The left endpoint retains the pre-existing x2842..2874 transition outside the adopted scope. This local repair does not certify that old endpoint or the complete north edge.","The previously passed internal vertical seam x3072/y0..252 intersects this edit and was inspected within original-size fixed q0/bottom q0/full context; no new internal break found. Other internal seams and all junctions remain unchanged."]
  o["northJoin"]="Local far-east improvement only. Current published north edge still has unadopted partial24 and old endpoint issues; whole-edge status remains unresolved."
  o["frozenNW630Unchanged"]=True;o["partial10dUsed"]=False;o["latestPublishedStill"]="66848fcdb5ff648de5f448588dbb4cd1c70693dee07ea43f3b15da0ed353d377"
  o["remainingExternal"]="Retained old x2842/2874 northern transition and remaining north/west overall acceptance; local repair must not be counted as formal or full-edge acceptance."
 qp=d/"visual-qa.json";qp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");reports.append({"tile":tile,"visualQA":info(qp),"candidate":m["candidate"]})
 if tile=="r14_c14":
  resume=s/tile/"production-resume-20261012.json";r=json.loads(resume.read_text(encoding="utf-8-sig"));r["latestRootProducedOfflineTrial"]={"version":version,"native":m["native"],"receipt":m["receipt"],"candidate":m["candidate"],"composition":info(d/"composition.json"),"visualQA":info(qp),"status":"local_visual_pass_pending_root_review_unpublished","workerNetworkRetried":False,"publishedPointerUnchanged":True,"partial10dUsed":False};resume.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(reports))
