import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
import json,hashlib,re
from datetime import datetime,timezone
from PIL import Image
S=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest");OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(S));import checkpoint_resume as old
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
paths=sorted(set(p for p in S.rglob("*.json") if ("receipts" in p.parts or p.name.endswith(".receipt.json") or p.name=="receipt.json") and OUT not in p.parents and "audit-runs" not in p.parts))
cache={};items=[];issues=[]
for p in paths:
 try:
  r=read(p);raw=old.source_output(r);sup=old.supplemental_receipt_evidence(p,r,cache)
  status=r.get("status") or ("tool_error" if r.get("error") else "returned_image" if sup.get("nativeReturnVerified") else None)
  item={"receipt":str(p),"receiptSha256":sha(p),"status":status,"output":str(raw) if raw else None,"disposition":r.get("rejectionReason") or r.get("visualDisposition") or r.get("disposition") or r.get("reason"),"explicitRejected":bool(r.get("rejectionReason")) or r.get("accepted")==False or str(r.get("visualDisposition","")).lower().startswith("rejected") or "rejected" in p.parts or sup.get("explicitlyRejected",False),"supplement":sup}
  if raw and raw.exists():
   item["image"]=old.image_info(raw,cache)
   if not status and not r.get("error"):item["status"]="returned_image_verified_file"
  items.append(item)
 except Exception as e:issues.append({"receipt":str(p),"error":str(e)})
result={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"receiptCount":len(items),"statuses":dict(Counter(x["status"] for x in items)),"receipts":items,"issues":issues}
(OUT/"receipt-discovery.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"receipts":len(items),"statuses":result["statuses"],"issues":issues}))
for i,x in enumerate(items):
 print(i,str(Path(x["receipt"]).relative_to(S)),x["status"],(x.get("image") or {}).get("sha256","")[:10],"REJECT" if x["explicitRejected"] else "",str(x["disposition"] or "")[:150])

