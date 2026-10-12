import json,hashlib
from pathlib import Path
z=Path(__file__).resolve().parent
rows=json.loads((z/"right-current-selection-20261012.json").read_text(encoding="utf8"))["tiles"]["r06_c04"]["matrix"]
m={"schemaVersion":1,"tileId":"r06_c04","nativePixels":1254,"corePixels":1024,"haloPixels":115,"patchMatrix":[]}
for r,row in enumerate(rows,1):
    entries=[]
    for c,a in enumerate(row,1):
        assert a is not None
        p=f"native/r06_c04_s{r:02d}_{c:02d}_{a}.png"
        entries.append({"path":p,"generationRecord":p+".generation.json","sha256":hashlib.sha256((z/p).read_bytes()).hexdigest()})
    m["patchMatrix"].append(entries)
out=z/"r06_c04.candidate-v1.manifest.json";assert not out.exists()
out.write_text(json.dumps(m,indent=2)+"\n",encoding="utf8")
print(out)

