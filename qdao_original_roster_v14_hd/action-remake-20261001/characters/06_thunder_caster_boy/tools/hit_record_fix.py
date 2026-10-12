from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
for p in (R/"work").glob("hit_*.png.generation.json"):
 r=json.loads(p.read_text(encoding="utf-8")); src=p.with_name(p.name.removesuffix(".generation.json")); times=re.findall(rb"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z",src.read_bytes()[:100000]); r["generatedAt"]=times[0].decode() if times else r.get("generatedAt");
 if not (src.name.startswith("hit_E_02_") or src.name.startswith("hit_W_02_")):
  ref=R/("work/hit_E_00_v1.png" if src.name=="hit_E_05_v2.png" else ("work/hit_W_00_v1.png" if src.name=="hit_W_05_v2.png" else ("work/hit_W_02_v1.png" if src.name.startswith("hit_W_") else "work/hit_E_02_v1.png"))); extra={"path":str(ref),"role":"adjacent same-direction hit key pose continuity reference","sha256":hashlib.sha256(ref.read_bytes()).hexdigest()}; r["references"]=[x for x in r["references"] if x["path"]!=str(ref)]+[extra]; r["submittedParameters"]["referenced_image_paths"]=[x["path"] for x in r["references"]]
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 if r.get("exportPath"):
  q=R/(r["exportPath"]+".generation.json"); d=json.loads(q.read_text(encoding="utf-8")); d["generatedAt"]=r["generatedAt"]; q.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("hit metadata synchronized")

