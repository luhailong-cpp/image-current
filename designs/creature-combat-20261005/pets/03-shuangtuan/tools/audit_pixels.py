from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
root=Path(__file__).resolve().parents[1]
rows=[];duplicates={};edge=[];index=["# 逐图生成记录索引","","目标 gpt-image-2.5-sunburst/max；实际 model/quality 均由各图记录说明。字段为 null 表示工具未披露，不能按目标回填。","","|动作|方向|帧|正式图片|来源记录|SHA256|","|---|---|---:|---|---|---|"]
for action,count in [("hit",6),("attack",12),("cast",16)]:
 for d in ("E","W"):
  for i in range(1,count+1):
   file=f"runtime/{action}/{d}/{i:02}.png";p=root/file
   if not p.exists():continue
   record=f"records/{action}/{d}/{i:02}.generation.json";j=json.loads((root/record).read_text(encoding="utf-8"))
   with Image.open(p) as im:
    im=im.convert("RGBA"); alpha=im.getchannel("A"); threshold=alpha.point(lambda n:255 if n>=128 else 0)
    bbox=threshold.getbbox(); borders=list(alpha.crop((0,0,1024,1)).getdata())+list(alpha.crop((0,1023,1024,1024)).getdata())+list(alpha.crop((0,0,1,1024)).getdata())+list(alpha.crop((1023,0,1024,1024)).getdata())
    pixel=hashlib.sha256(im.tobytes()).hexdigest();duplicates.setdefault(pixel,[]).append(file)
    row={"file":file,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"pixelSha256":pixel,"alphaExtrema":alpha.getextrema(),"subjectAlpha128Bounds":bbox,"outerEdgePixelsAlphaAbove8":sum(v>8 for v in borders),"maxOuterAlpha":max(borders),"size":im.size,"actualModel":j.get("actualModel"),"actualQuality":j.get("actualQuality")}
    if row["sha256"]!=j["sha256"]:raise ValueError("Mismatch "+file)
    rows.append(row)
    if row["outerEdgePixelsAlphaAbove8"]:edge.append(row)
   index.append(f"|{action}|{d}|{i:02}|[{i:02}.png]({file})|[generation]({record})|{row['sha256']}|")
report={"createdAt":datetime.now(timezone.utc).isoformat(),"count":len(rows),"expected":68,"all68":len(rows)==68,"pixelDuplicateSets":[v for v in duplicates.values() if len(v)>1],"edgeReview":edge,"frames":rows,"scope":"Pixels, hashes and alpha only; no dynamic visual or client pass inferred."}
(root/"qa"/"pixel-alpha-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"generation-index.md").write_text("\n".join(index)+"\n",encoding="utf-8")
print(json.dumps({"count":len(rows),"pixelDuplicates":report["pixelDuplicateSets"],"edgesAbove8":[{"file":x["file"],"pixels":x["outerEdgePixelsAlphaAbove8"],"max":x["maxOuterAlpha"]} for x in edge]}))

