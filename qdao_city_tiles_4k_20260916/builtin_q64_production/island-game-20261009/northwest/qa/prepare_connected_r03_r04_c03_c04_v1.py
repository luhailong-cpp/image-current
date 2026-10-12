from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=[("r03_c03","v5","f928ee","f17412"),("r03_c04","v5","5ee844d5","054214cc"),("r04_c03","v5","b2c762b0",None),("r04_c04","v4","ac3cab03","f7fb54e8")]
items=[]
for tid,v,ph,rh in spec:
 p=Z/"tiles"/f"{tid}_candidate-{v}_4096.png";r=Z/"tiles"/f"{tid}_candidate-{v}_4096.native-repair.json"
 a,b=sha(p),sha(r);assert a.startswith(ph),(tid,a);assert rh is None or b.startswith(rh),(tid,b)
 items.append({"tileId":tid,"image":{"path":str(p),"sha256":a},"record":{"path":str(r),"sha256":b}})
m={"schemaVersion":1,"tileMatrix":[items[:2],items[2:]],"status":"four explicit internally-reviewed candidates for native boundary source selection; external visual QA still pending"}
p=Z/"qa/connected-r03-r04-c03-c04-v1.input-manifest.json"
with p.open("x",encoding="utf-8") as f:json.dump(m,f,ensure_ascii=False,indent=2)
print(json.dumps({"manifest":str(p),"tiles":items},ensure_ascii=False))

