import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Z))
from assemble_tile import load_raw_source
stems=["r04_c04_s01_01_a07","r04_c04_s02_01_a02","r04_c04_s03_01_a02","r04_c04_s04_01_a01","r04_c04_s02_02_a02","r04_c04_s03_02_a02","r04_c04_s04_02_a01"]
out=[]
for s in stems:
 r,c=map(int,s.split("_s")[1].split("_a")[0].split("_"))
 p=Z/"native"/(s+".png"); g=p.with_name(p.name+".generation.json")
 record,arr=load_raw_source(p.resolve(),g.resolve(),"r04_c04",r-1,c-1)
 out.append({"stem":s,"row":r,"col":c,"path":str(p),"sha256":record["sha256"],"generationRecord":str(g),"generationSha256":record["generationRecord"]["sha256"],"nativeSize":list(arr.shape[:2][::-1]),"strictRawSourceValidation":"passed"})
qa=["r04_c04_s01_01_a07_left","r04_c04_s01_01_a07_top","r04_c04_s01_01_a07_right","r04_c04_s01_01_a07_bottom","r04_c04_s02_01_a02_left","r04_c04_s03_01_a02_top_a02","r04_c04_s03_01_a02_left","r04_c04_s04_01_a01_left","r04_c04_s04_01_a01_top","r04_c04_s02_02_a02_left","r04_c04_s02_02_a02_top","r04_c04_s03_02_a02_left","r04_c04_s03_02_a02_top","r04_c04_s04_02_a01_left","r04_c04_s04_02_a01_top"]
data={"schemaVersion":1,"tileId":"r04_c04","owner":"diagonal_tile_resume","createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"explicit_native_selection_for_parent_assembly_pending_whole_tile_and_cross4k_review","selection":out,"qaDirectories":[str(Z/"qa"/q) for q in qa],"visualReview":{"scale":"native 100 percent seam crops; no resampling","hardMinerror":"listed pairs reviewed; internal paving/wall/tree continuity usable except listed outstanding shared issues","fixedCore115":"checked s01_01 left/top/bottom, s02_02 left/top, s03_02 left/top, s04_02 left/top; rigid115 cut exposes tonal or microtexture straight boundaries in several pairs, prefer reviewed binary minimum-error native source seam","noFeatherOrColorCorrection":True},"resolved":["s01_01a07 removes the internal x230 pasted rectangle from a06 while maintaining wall entrance and ball cap geometry","s02_01a02 restores railing continuation on right behind pillar","s03_01a02 preserves gold roof edge entrance low in patch instead of lifting the roof","s03_02a02 repairs blurry corner foliage to consistent game-map focus"],"outstandingSharedIssues":[{"location":"s01_01 to s01_02 right seam and inside s01_02","issue":"existing paving/grass edge backtrack and short stone-grid transition; parent already noted; inspect in whole tile","qa":str(Z/"qa/r04_c04_s01_01_a07_right/hard_minerror_native_seam100pct.png")},{"location":"r04_c03 to r04_c04 lower-left roof/lantern crossing","issue":"left tile now v5 roof repair changes east boundary y2762..3776; original s04_01 left seam has lantern silhouette cut against white wall, requires cross4k joint QA/repair","qa":str(Z/"qa/r04_c04_s04_01_a01_left/hard_minerror_native_seam100pct.png")},{"location":"second row railing global trajectory","issue":"s02_02 follows native left wall but arrives at right y790 versus blurred guide about650; review continuous full railing with parent-generated right columns"}],"guardrails":{"builtinOnly":True,"paidApiUsed":False,"finalArtResized":False,"sharedProgressModified":False,"sharedSelectedManifestModified":False,"formalAcceptanceClaim":False}}
dest=Z/"qa/r04_c04_diagonal_agent_selection_v1.json"
with dest.open("x",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps({"report":str(dest),"selectionCount":len(out),"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"validation":"all 7 strict raw source checks passed"}))

