from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[];errors=[]
for d,n in [("E",12),("W",6)]:
 for i in range(1,n+1):
  p=B/"runtime"/"attack"/d/f"{i:02d}.png"
  recpath=p.with_suffix(".png.generation.json")
  if not p.exists() or not recpath.exists():errors.append(str(p)+" missing image or record");continue
  rec=json.loads(recpath.read_text(encoding="utf-8-sig"))
  with Image.open(p) as im:
   a=im.getchannel("A");solid=a.point(lambda x:255 if x>=128 else 0);bbox=solid.getbbox()
   edge=list(a.crop((0,0,im.width,1)).getdata())+list(a.crop((0,im.height-1,im.width,im.height)).getdata())+list(a.crop((0,0,1,im.height)).getdata())+list(a.crop((im.width-1,0,im.width,im.height)).getdata())
   item={"file":str(p),"width":im.width,"height":im.height,"mode":im.mode,"sha256":sha(p),"alphaExtrema":a.getextrema(),"opaqueBounds":bbox,"edgeAlphaMax":max(edge),"promptExists":Path(rec["prompt"]).exists(),"receiptExists":Path(rec["evidence"]["receipt"]).exists(),"sourceReferenceHashesMatch":all(Path(r["path"]).exists() and sha(r["path"])==r["sha256"] for r in rec["references"]),"nativeSourceHashMatch":sha(rec["nativeSourcePath"])==rec["native"]["sha256"],"recordHashMatch":sha(p)==rec["export"]["sha256"]}
   if im.size!=(1024,1024) or im.mode!="RGBA" or a.getextrema()!=(0,255):errors.append(str(p)+" dimensions/alpha failure")
   if not all(item[k] for k in ("promptExists","receiptExists","sourceReferenceHashesMatch","nativeSourceHashMatch","recordHashMatch")):errors.append(str(p)+" reference/hash failure")
   items.append(item)
hashes=[x["sha256"] for x in items]
if len(set(hashes))!=len(hashes):errors.append("duplicate final file hashes")
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Attack E01-12 and W01-06, before parent uniform-direction final export","expectedCount":18,"actualCount":len(items),"uniqueHashes":len(set(hashes)),"errors":errors,"result":"passed" if not errors else "failed","frameVisualReview":"All 18 final native outputs actually viewed individually. E07 repaired for far wing reaching edge. Full sequence playback and common-direction anchoring pending parent review.","runtimeIntegration":"not tested","items":items}
(B/"provenance"/"attack"/"validation-assigned.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"result":report["result"],"count":len(items),"unique":report["uniqueHashes"],"errors":errors,"edgeNonzero":[{"frame":Path(x["file"]).parent.name+"/"+Path(x["file"]).name,"edgeAlphaMax":x["edgeAlphaMax"],"opaqueBounds":x["opaqueBounds"]} for x in items if x["edgeAlphaMax"]>0]},ensure_ascii=False))

