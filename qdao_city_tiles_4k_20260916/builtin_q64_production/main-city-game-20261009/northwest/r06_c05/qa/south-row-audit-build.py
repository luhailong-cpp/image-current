import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest"); sys.path.insert(0,str(B));import assemble_native as a
O=B/"r06_c05"/"qa";O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sels={t:json.loads((B/t/"selection.json").read_text(encoding="utf-8-sig")) for t in ["r06_c04","r06_c05"]}
pids=[("r06_c04","s04_04")]+[("r06_c05",f"s04_{i:02}") for i in range(1,5)]
sources=[]
for t,pid in pids:
 p=Path(sels[t][pid]);record=p.with_suffix(".png.generation.json");r=json.loads(record.read_text(encoding="utf-8-sig"))
 im=Image.open(p);assert im.size==(1254,1254) and sha(p)==r["sha256"]
 e=r["evidence"];receipt=Path(e["receipt"]);request=Path(e["request"]);rp=json.loads(receipt.read_text(encoding="utf-8-sig"));rq=json.loads(request.read_text(encoding="utf-8-sig"))
 assert receipt.exists() and request.exists()
 sources.append({"tile":t,"logicalId":pid,"file":str(p),"sha256":sha(p),"generationRecord":str(record),"generationRecordSha256":sha(record),"receipt":str(receipt),"receiptSha256":sha(receipt),"receiptFields":list(rp),"request":str(request),"requestSha256":sha(request),"actualModel":r["actualModel"],"actualQuality":r["actualQuality"],"dimensions":list(im.size)})
reports=[]
for i in range(4):
 left,right=sources[i:i+2];A=np.asarray(Image.open(left["file"]).convert("RGB"));C=np.asarray(Image.open(right["file"]).convert("RGB"))
 joint,seam=a.append_with_minimum_seam(A,C)
 # Full 1254 native vertical boundary, showing 200 pixels each side, transposed solely for display.
 hard=np.concatenate([A[:,939:1139],C[:,115:315]],axis=1).transpose(1,0,2)
 minimum=joint[:,939:1339].transpose(1,0,2)
 canvas=Image.new("RGB",(1254,848),"#202020");canvas.paste(Image.fromarray(hard),(0,24));canvas.paste(Image.fromarray(minimum),(0,448));d=ImageDraw.Draw(canvas);d.text((5,5),"FULL 1254px boundary; HARD CUT. Display x = source y, display y = source x.",fill="white");d.text((5,429),"MINIMUM-ERROR BINARY SOURCE SELECTION; no resize, blending or color edit",fill="white")
 name="external-west" if i==0 else f"internal-c{i}-c{i+1}"
 out=O/("south-row-audit-"+name+".png");canvas.save(out)
 diff=np.abs(A[:,-230:].astype(float)-C[:,:230])
 reports.append({"name":name,"left":left,"right":right,"output":str(out),"outputSha256":sha(out),"nativeBoundaryLength":1254,"fullOverlapWidth":230,"overlapMeanAbsoluteRGBDifference":float(diff.mean()),"overlapP95":float(np.percentile(diff,95)),"seamMinMax":[int(seam.min()),int(seam.max())],"nativeScale":1,"actuallyViewed":False})
(O/"south-row-audit-evidence.json").write_text(json.dumps({"sources":sources,"pairs":reports},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"sources":sources,"pairs":[{k:v for k,v in r.items() if k not in ["left","right"]} for r in reports]},indent=2))

