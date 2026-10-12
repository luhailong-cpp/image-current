from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
tile,patch,attempt,prefix=sys.argv[1:];T=B/tile;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/"pipeline/prompts"/(patch+".resumed-full64-v01.request.json")
req=json.loads(base.read_text());target=T/"guides"/(patch+".layout-only.png")
prompt=Path(prefix).read_text(encoding="utf-8-sig");pp=T/"pipeline/prompts"/(patch+"."+attempt+".prompt.txt");rp=T/"pipeline/prompts"/(patch+"."+attempt+".request.json")
assert not pp.exists() and not rp.exists();pp.write_text(prompt,encoding="utf-8")
req.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),neighborSources=[],cornerTreatment={"bothSourcesPresent":False,"reason":"Macro layout repair takes precedence over known inconsistent previous neighbor strips; shared borders require coordinated QA."})
req["references"][0]={"file":str(target),"sha256":sha(target),"role":"approved-layout exact crop; coarse guide only, create native detail"}
extra=B/"pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png"
req["references"].append({"file":str(extra),"sha256":sha(extra),"role":"approved quiet stone material crop only"})
req["referenced_image_paths"]=[r["file"] for r in req["references"]]
req["boundaryRepairRequired"]=True;atomic_json(rp,req);print(str(rp))
