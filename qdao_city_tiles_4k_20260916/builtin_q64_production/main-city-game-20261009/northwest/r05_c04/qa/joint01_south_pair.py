from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c04"); sys.path.insert(0,str(B.parent)); import assemble_native as asm
old=np.array(Image.open(B/"native/s04_02.png").convert("RGB"))
new=np.array(Image.open(B/"native/s04_02_joint01.png").convert("RGB"))
southpath=B.parent/"r06_c04/native/s01_02.png"
south=np.array(Image.open(southpath).convert("RGB"))
report={"neighborFile":str(southpath),"neighborSha256":hashlib.sha256(southpath.read_bytes()).hexdigest(),"generatedPatchIsNotPixelIdenticalInPreservedSouth":True,"pairs":[]}
for name,a in [("old",old),("joint01",new)]:
 out,seam=asm.append_with_minimum_seam(a.transpose(1,0,2),south.transpose(1,0,2))
 out=out.transpose(1,0,2)
 file=B/"qa"/("s04_02_joint01-south-pair-"+name+".png")
 Image.fromarray(out[979:1299,115:1139]).save(file)
 d=np.abs(a[1024:].astype(float)-south[:230].astype(float))
 report["pairs"].append({"version":name,"seamStrip":str(file),"overlapMAE":float(d.mean()),"overlapP95":float(np.percentile(d,95)),"cutPath":seam.tolist(),"pixelEditing":"minimum-error binary source selection, no rescale/filter/blending"})
(B/"qa/s04_02_joint01-south-pair-metrics.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps([{k:v for k,v in a.items() if k!="cutPath"} for a in report["pairs"]],indent=2))

