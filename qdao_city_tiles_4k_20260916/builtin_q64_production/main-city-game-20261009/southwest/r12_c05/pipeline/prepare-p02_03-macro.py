from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];D=B/"pipeline";SW=B.parent
sys.path.insert(0,str(SW));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((D/"prompts/p02_03.resumed-full64-v01.request.json").read_text())
target=B/"guides/p02_03.layout-only.png"
prompt="""Render ONLY the pale gray pavement close-up in IMAGE1 into a crisp new native1254x1254 image. The coarse pixels define a precise cropped layout, not a full scene. Exactly THREE narrow straight grout segments: (A) a short diagonal from top(926,0) to right(1254,220); (B) the main diagonal from right(1254,240) down-left to an intersection at(168,997); (C) a continuous diagonal from left(0,885) through that intersection(168,997) to bottom(544,1254). SegmentB meets segmentC at the lower-left T junction; it does not continue through. These are ordinary thin joints between huge flat stone slabs, no broad inlaid stripe, no additional grid or joints. Material: almost featureless smooth satin-matte pale gray limestone like the quiet broad faces in IMAGE5. Each huge face has3-5 broad soft tonal areas, each more than250px. No tiny marks smaller than80px: no woven crosshatching,cells,scales,grain,noise,dabs,veins or cracks. Keep edges crisp and subtly rounded. All images2-4 are context/style references only; copy no buildings,objects,ornaments,scene,text or red paper from them. Entire output is only this same flat ground crop. Preserve the exact line topology and near-blank large slabs."""
pp=D/"prompts/p02_03.macro-topology-v01.prompt.txt";rp=D/"prompts/p02_03.macro-topology-v01.request.json"
assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding="utf-8")
req.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),neighborSources=[],cornerTreatment={"bothSourcesPresent":False,"reason":"Existing selected top/left native strips omit real macro grout; regenerate correct topology, then coordinate neighbor repair."})
req["references"][0]={"file":str(target),"sha256":sha(target),"role":"exact approved layout crop, nearest guide only; generate real native art not upscale"}
extra=SW/"pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png"
req["references"].append({"file":str(extra),"sha256":sha(extra),"role":"quiet stone material-only crop from approved detail reference"})
req["referenced_image_paths"]=[r["file"] for r in req["references"]]
req["boundaryRepairRequired"]=["p01_03 lower-right","p02_02 lower-right"]
atomic_json(rp,req);print(str(rp))
