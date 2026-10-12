from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent;SW=B.parent
sys.path.insert(0,str(SW));from checkpoint_resume import atomic_json
patch=sys.argv[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=B/"native"/(patch+".png")
record=json.loads(Path(str(source)+".generation.json").read_text())
base=json.loads(Path(record["request"]).read_text())
prompt="""Edit only IMAGE1. Replace its entire woven/cellular/crosshatched stone texture with almost featureless, smooth, satin-matte pale gray limestone, matching the quiet broad stone faces in IMAGE5. Keep EVERY EXISTING grout segment and intersection exactly where it is. Do not add, remove, thicken or move any line. Keep the full1254 square framing and light-gray color. Each stone face must have only3-5 very broad soft irregular tonal areas, each more than250pixels across. No visible texture mark smaller than80pixels: no dabs, grain, mesh, crosshatch, scales, stippling, cells, cracks or tiny details. It is naturally smooth stone at extreme close range. Preserve crisp grout edges and restrained bevels; the material itself stays quiet. All of images2,3,4 are contextual style/layout references only: copy no object, architecture, ornament, scene or text from them. Output only this same pale-gray stone closeup."""
pp=D/(patch+"-quiet-material-v01.prompt.txt");rp=D/(patch+"-quiet-material-v01.request.json")
assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding="utf-8")
base.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat())
base["references"][0]={"file":str(source),"sha256":sha(source),"role":"edit target, change stone face material only; all line topology invariant"}
extra=SW/"pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png"
base["references"].append({"file":str(extra),"sha256":sha(extra),"role":"quiet stone material-only crop from approved detail reference"})
base["referenced_image_paths"]=[r["file"] for r in base["references"]]
base["materialRepair"]=True;atomic_json(rp,base);print(str(rp))
