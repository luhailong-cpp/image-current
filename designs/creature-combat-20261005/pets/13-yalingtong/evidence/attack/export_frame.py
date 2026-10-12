import json, re, hashlib, sys
from pathlib import Path
from PIL import Image
base=Path(__file__).resolve().parents[2]
direction, num=sys.argv[1],sys.argv[2]
stem=f"{direction}/{int(num):02d}"
rp=base/"evidence/attack"/f"{stem}.receipt.json"
r=json.loads(rp.read_text(encoding="utf-8"))
src=Path(re.search(r" as (C:.*?\.png) by default",r["output_hint"]).group(1))
im=Image.open(src); native={"width":im.width,"height":im.height,"mode":im.mode,"format":im.format,"sha256":hashlib.sha256(src.read_bytes()).hexdigest()}
out=base/"runtime/attack"/f"{stem}.png"; out.parent.mkdir(parents=True,exist_ok=True)
im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
r.update({"file":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"native":native,"sourcePath":str(src),"generatedAt":r["completedAt"],"width":1024,"height":1024,"format":"PNG","configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8")),"prompt":str(base/"prompts/attack"/f"{stem}.txt"),"references":[{"path":x,"sha256":hashlib.sha256(Path(x).read_bytes()).hexdigest(),"role":("previous_attack_edit_target" if i==4 else "corrected_W_foot_orientation" if i==3 else "primary_style" if i==2 else "identity_E" if i==0 else "identity_W")} for i,x in enumerate(r["submittedParameters"]["referenced_image_paths"])],"derivedFrom":{"path":str(src),"sha256":native["sha256"]},"operation":"Uniform full-canvas resize to 1024x1024; no crop, frame alignment, mirror, interpolation or pose fabrication.","visualQA":{"status":"inspected_generated_frame","notes":sys.argv[3] if len(sys.argv)>3 else ""}})
out.with_suffix(".png.generation.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"saved":str(out),"native":native,"alpha":Image.open(out).getchannel("A").getextrema()},ensure_ascii=False))

