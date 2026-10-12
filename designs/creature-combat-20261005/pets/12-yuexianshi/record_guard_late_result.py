"""Record actual built-in edit results; optionally export through the shared transform."""
import sys,json,hashlib,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent
d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
tag=d["tag"]; group="attack-W"
source=Path(d["source"])
refs=[dict(path=p,role=role,**({"historicalGenerationInput":True} if i>2 else {})) for i,(p,role) in enumerate(zip(d["refs"],["original E identity","original W identity","approved painted materials","edit target; preserve frame-specific upper body","guard stance reference; legs only"]))]
job=dict(action="attack",direction="W",index=d["index"],source=str(source),generatedAt=d["generatedAt"],prompt=f"prompts/{group}/{tag}.txt",receipt=f"records/{group}/{tag}.receipt.json",references=refs,visualStatus=d["visualStatus"])
receipt=dict(tool="image_gen.imagegen",route="builtin",generatedAt=d["generatedAt"],submittedParameters=dict(model=None,quality=None,prompt=d["prompt"],referenced_image_paths=d["refs"],transparent_background=True),actualModel=None,actualQuality=None,returned=dict(output_hint=d["output_hint"],imageDataOmitted=True))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
jobpath=ROOT/f"records/{group}/{tag}.job.json"
save(jobpath,job);save(ROOT/job["receipt"],receipt)
(ROOT/job["prompt"]).write_text(d["prompt"],encoding="utf-8")
nativepath=ROOT/f"records/{group}/{tag}.generation.json"
subprocess.run([sys.executable,str(ROOT/"record_native_candidate.py"),str(jobpath),str(nativepath)],check=True)
native=json.loads(nativepath.read_text(encoding="utf-8"));native["disposition"]="selected-final" if d.get("export") else "rejected-candidate";save(nativepath,native)
if d.get("export"):subprocess.run([sys.executable,str(ROOT/"export_frame.py"),str(jobpath)],check=True)
