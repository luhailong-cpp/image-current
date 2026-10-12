import json,re
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"work/keyposes_E_v1.png.generation.json"
r=json.loads(p.read_text(encoding="utf-8")); r["native"]["perFrameWidth"]=627; r["native"]["perFrameHeight"]=627; r["native"]["layout"]=[2,2]; p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=Path(__file__).resolve().parents[1]/"work/hit_E_02_v1.png.generation.json"
r=json.loads(p.read_text(encoding="utf-8")); times=re.findall(rb"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z",p.with_name("hit_E_02_v1.png").read_bytes()[:100000]); r["generatedAt"]=times[0].decode() if times else None; p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(r["generatedAt"])

