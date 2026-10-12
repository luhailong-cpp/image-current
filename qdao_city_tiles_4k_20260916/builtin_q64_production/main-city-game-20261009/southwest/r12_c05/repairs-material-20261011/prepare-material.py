from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent;SW=B.parent
sys.path.insert(0,str(SW));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/"native/p01_02.png";p=D/"p01_02-quiet-material-v01.prompt.txt";r=D/"p01_02-quiet-material-v01.request.json"
prompt="""Edit only IMAGE1. Replace its entire woven/cellular/crosshatched stone texture with almost featureless, smooth, satin-matte pale gray limestone, matching the quiet broad stone faces in IMAGE5. Keep the ONE tiny diagonal grout fragment clipped at the upper-left exactly where it is; do not add any other lines. Keep the full1254 square framing and light-gray color. The surface must have only3-5 very broad soft irregular tonal areas, each more than250pixels across. No visible mark smaller than80pixels: no dabs, grain, mesh, crosshatch, scales, stippling, cells, cracks or tiny details. It is naturally smooth stone at extreme close range. Preserve a crisp grout edge; the material itself stays quiet, not noisy. All of images2,3,4 are contextual style/layout references only: copy no object, architecture, ornament, scene or text from them. Output only this same near-blank light gray stone closeup."""
p.write_text(prompt,encoding="utf-8")
req=json.loads((B/"pipeline/prompts/p01_02.restored20261011-v02.request.json").read_text())
req.update(prompt=prompt,promptFile=str(p),promptSha256=sha(p),preparedAtUtc=datetime.now(timezone.utc).isoformat())
req["references"][0]={"file":str(source),"sha256":sha(source),"role":"edit target, replace material only"}
extra=SW/"pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png"
req["references"].append({"file":str(extra),"sha256":sha(extra),"role":"material-only crop from approved detail reference, preserve quiet broad stone faces"})
req["referenced_image_paths"]=[x["file"] for x in req["references"]]
req["materialRepair"]=True
atomic_json(r,req)
print(str(r))
